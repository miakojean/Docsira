import os
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import AffairSerializer, DocumentSerializer
from .models import Affair, Document

class BaseFirmView(APIView):
    """Classe utilitaire pour récupérer le véritable compte du cabinet"""
    def get_firm(self, user):
        if hasattr(user, 'collaborator_profile'):
            return user.collaborator_profile.main_account
        return user

class AffairView(BaseFirmView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AffairSerializer(data=request.data)
        if serializer.is_valid():
            # Assigne l'affaire au vrai compte du cabinet au lieu du request.user[cite: 3, 4]
            firm = self.get_firm(request.user)
            serializer.save(firm=firm) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, affair_id=None):
        firm = self.get_firm(request.user)

        if affair_id:
            try:
                # Filtrage unifié basé sur la Firme[cite: 3]
                affair = Affair.objects.get(id=affair_id, firm=firm)
                serializer = AffairSerializer(affair)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Affair.DoesNotExist:
                return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            affairs = Affair.objects.filter(firm=firm)
            client_id = request.query_params.get('client')
            if client_id:
                affairs = affairs.filter(client_id=client_id)
            
            paginator = PageNumberPagination()
            paginator.page_size = 10 
            paginated_affairs = paginator.paginate_queryset(affairs, request)
            serializer = AffairSerializer(paginated_affairs, many=True)
            return paginator.get_paginated_response(serializer.data)

    def patch(self, request, affair_id):
        try:
            firm = self.get_firm(request.user)
            affair = Affair.objects.get(id=affair_id, firm=firm)
            serializer = AffairSerializer(affair, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, affair_id):
        try:
            firm = self.get_firm(request.user)
            affair = Affair.objects.get(id=affair_id, firm=firm)
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


class AffairDocumentsView(BaseFirmView):
    """Liste et ajoute plusieurs documents dans un dossier du cabinet."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_affair(self, request, affair_id):
        try:
            affair = Affair.objects.get(pk=affair_id)
        except Affair.DoesNotExist:
            return None, Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if affair.firm_id != self.get_firm(request.user).id:
            return None, Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        return affair, None

    def get(self, request, affair_id):
        affair, error_response = self.get_affair(request, affair_id)
        if error_response:
            return error_response

        documents = affair.documents.all()
        return Response(DocumentSerializer(documents, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, affair_id):
        affair, error_response = self.get_affair(request, affair_id)
        if error_response:
            return error_response

        files = request.FILES.getlist("files") or request.FILES.getlist("file")
        if not files:
            return Response(
                {"files": "Sélectionnez au moins un fichier à ajouter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializers = []
        for uploaded_file in files:
            file_name = os.path.basename(uploaded_file.name.replace("\\", "/"))
            title = os.path.splitext(file_name)[0].strip() or file_name
            serializer = DocumentSerializer(data={
                "affair": str(affair.pk),
                "title": title[:200],
                "file": uploaded_file,
            })
            if not serializer.is_valid():
                return Response(
                    {"files": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializers.append(serializer)

        created_documents = []
        previous = affair.documents.order_by("-uploaded_at").first()
        with transaction.atomic():
            for serializer in serializers:
                relation = Document.Relation.ADDED if previous else Document.Relation.INITIAL
                document = serializer.save(parent=previous, relation=relation, version=1)
                created_documents.append(document)
                previous = document
            _touch_affair(affair)

        return Response(
            DocumentSerializer(created_documents, many=True).data,
            status=status.HTTP_201_CREATED,
        )

class DocumentView(BaseFirmView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            firm = self.get_firm(request.user)
            affair = serializer.validated_data['affair']
            
            # Vérification de sécurité : le dossier appartient-il au cabinet ?
            if affair.firm != firm:
                return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, doc_id=None):
        firm = self.get_firm(request.user)

        if doc_id:
            try:
                document = Document.objects.get(id=doc_id, affair__firm=firm)
                serializer = DocumentSerializer(document)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Document.DoesNotExist:
                return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            documents = Document.objects.filter(affair__firm=firm)
            affair_id = request.query_params.get('affair')
            if affair_id:
                documents = documents.filter(affair_id=affair_id)

            paginator = PageNumberPagination()
            paginator.page_size = 10 
            paginated_documents = paginator.paginate_queryset(documents, request)
            serializer = DocumentSerializer(paginated_documents, many=True)
            return paginator.get_paginated_response(serializer.data)