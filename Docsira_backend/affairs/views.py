import math
import os
from django.core.exceptions import ValidationError
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import AffairSerializer, DocumentSerializer
from .models import Affair, Document
# Create your views here.

class AffairView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AffairSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(firm=request.user)  # Assuming the firm is the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, affair_id=None):
        if affair_id:
            try:
                affair = Affair.objects.get(id=affair_id, firm=request.user)
                serializer = AffairSerializer(affair)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Affair.DoesNotExist:
                return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            affairs = Affair.objects.filter(firm=request.user)
            client_id = request.query_params.get('client')
            if client_id:
                affairs = affairs.filter(client_id=client_id)
            
            # 2. Configuration et application de la pagination
            paginator = PageNumberPagination()
            paginator.page_size = 10 # Définit le nombre de dossiers par page
            
            # 3. Découpage du QuerySet
            paginated_affairs = paginator.paginate_queryset(affairs, request)
            
            # 4. Sérialisation des données paginées uniquement
            serializer = AffairSerializer(paginated_affairs, many=True)
            
            # 5. Renvoi d'une réponse structurée avec les métadonnées de pagination
            return paginator.get_paginated_response(serializer.data)

    def patch(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id, firm=request.user)
            serializer = AffairSerializer(affair, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id, firm=request.user)
            affair.delete()
            return Response({"message": "Affair deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

# N'oubliez pas l'import si ce n'est pas déjà fait en haut de votre fichier :
# from rest_framework.pagination import PageNumberPagination

def _touch_affair(affair):
    """Marque une activité sur le dossier ; un dossier NOUVEAU passe EN_COURS."""
    fields_to_update = ['last_activiation_date']
    if affair.statut == 'NOUVEAU':
        affair.statut = 'EN_COURS'
        fields_to_update.append('statut')
    affair.save(update_fields=fields_to_update)


class DocumentView(APIView):
    """Liste et ajout de documents d'un dossier (GET/POST /affairs/<affair_id>/documents/)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id, firm=request.user)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

        documents = affair.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, affair_id=None):
        """
        Accepte un ou plusieurs fichiers (champ `files` répété, ou `file`).
        `affair` peut venir de l'URL ou du corps (ancienne route /document/).
        """
        affair_id = affair_id or request.data.get('affair')
        try:
            affair = Affair.objects.get(id=affair_id, firm=request.user)
        except (Affair.DoesNotExist, ValueError, ValidationError):
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('files') + request.FILES.getlist('file')
        if not files:
            return Response({"error": "Aucun fichier fourni."}, status=status.HTTP_400_BAD_REQUEST)

        # Les nouveaux documents sont reliés au dernier document du dossier : c'est ce
        # qui dessine l'évolution du dossier dans l'espace de travail.
        last_document = affair.documents.order_by('-uploaded_at').first()
        relation = Document.Relation.ADDED if last_document else Document.Relation.INITIAL

        single_title = request.data.get('title') if len(files) == 1 else None
        created = []
        for uploaded in files:
            title = single_title or os.path.splitext(uploaded.name)[0]
            document = Document.objects.create(
                affair=affair, title=title[:200], file=uploaded,
                parent=last_document, relation=relation,
            )
            created.append(document)

        _touch_affair(affair)
        serializer = DocumentSerializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentDetailView(APIView):
    """Renommage et suppression d'un document (/affairs/documents/<document_id>/)."""

    permission_classes = [IsAuthenticated]

    def _get_document(self, request, document_id):
        return Document.objects.get(id=document_id, affair__firm=request.user)

    def get(self, request, document_id):
        try:
            document = self._get_document(request, document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentSerializer(document).data, status=status.HTTP_200_OK)

    def patch(self, request, document_id):
        try:
            document = self._get_document(request, document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        update_fields = []

        if 'title' in data:
            title = (data.get('title') or '').strip()
            if not title:
                return Response({"title": ["Le titre est requis."]}, status=status.HTTP_400_BAD_REQUEST)
            document.title = title[:200]
            update_fields.append('title')

        # Position sur l'espace de travail
        for axis in ('pos_x', 'pos_y'):
            if axis in data:
                raw = data.get(axis)
                try:
                    value = None if raw is None else float(raw)
                except (TypeError, ValueError):
                    return Response({axis: ["Nombre attendu."]}, status=status.HTTP_400_BAD_REQUEST)
                if value is not None and not math.isfinite(value):
                    return Response({axis: ["Nombre attendu."]}, status=status.HTTP_400_BAD_REQUEST)
                setattr(document, axis, value)
                update_fields.append(axis)

        if not update_fields:
            return Response({"error": "Aucune modification fournie."}, status=status.HTTP_400_BAD_REQUEST)
        document.save(update_fields=update_fields)
        return Response(DocumentSerializer(document).data, status=status.HTTP_200_OK)

    def delete(self, request, document_id):
        try:
            document = self._get_document(request, document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        # On recolle la chaîne : les documents suivants se rattachent au précédent
        Document.objects.filter(parent=document).update(parent=document.parent)
        document.file.delete(save=False)  # supprime aussi le fichier physique
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentVersionView(APIView):
    """Dépose une nouvelle version d'un document (POST /affairs/documents/<document_id>/versions/).

    L'ancienne version est conservée : la nouvelle y est reliée (relation UPDATED).
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, document_id):
        try:
            source = Document.objects.select_related('affair').get(
                id=document_id, affair__firm=request.user
            )
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        uploaded = request.FILES.get('file') or request.FILES.get('files')
        if not uploaded and request.FILES:
            uploaded = next(iter(request.FILES.values()), None)

        if not uploaded:
            return Response({"error": "Aucun fichier fourni."}, status=status.HTTP_400_BAD_REQUEST)

        pos_x = request.data.get('pos_x')
        pos_y = request.data.get('pos_y')
        try:
            pos_x = float(pos_x) if pos_x is not None else None
            pos_y = float(pos_y) if pos_y is not None else None
        except (ValueError, TypeError):
            pos_x = None
            pos_y = None

        title = (request.data.get('title') or '').strip() or source.title

        new_version = Document.objects.create(
            affair=source.affair,
            title=title[:200],
            file=uploaded,
            parent=source,
            relation=Document.Relation.UPDATED,
            version=source.version + 1,
            pos_x=pos_x,
            pos_y=pos_y,
        )
        _touch_affair(source.affair)
        return Response(DocumentSerializer(new_version).data, status=status.HTTP_201_CREATED)


class DocumentDownloadView(APIView):
    """Téléchargement authentifié (/affairs/documents/<document_id>/download/)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id, affair__firm=request.user)
            handle = document.file.open('rb')
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        except (FileNotFoundError, ValueError):
            return Response({"error": "Fichier introuvable sur le disque."}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(handle, as_attachment=False, filename=os.path.basename(document.file.name))