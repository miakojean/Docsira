from datetime import timedelta
import io
import mimetypes
import os
import zipfile
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from django.http import FileResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    AffairCommentSerializer,
    AffairSerializer,
    AffairShareLinkSerializer,
    DocumentSerializer,
    DocumentShareLinkSerializer,
)
from .models import (
    Affair,
    AffairComment,
    AffairCommentRead,
    AffairShareLink,
    Document,
    DocumentShareLink,
    get_user_display_name,
    resolve_document_file_path,
)
from account.permissions import IsFirmEditorOrReadOnly, is_firm_admin
from sira.models import SiraFolderHistory


DOCUMENT_MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.gif': 'image/gif',
}


def _extract_first_error(errors, default="Données invalides."):
    if isinstance(errors, list) and errors:
        return _extract_first_error(errors[0], default)
    if isinstance(errors, dict):
        for value in errors.values():
            msg = _extract_first_error(value, None)
            if msg:
                return msg
        return default
    if errors is None:
        return default
    return str(errors)

class BaseFirmView(APIView):
    """Classe utilitaire pour récupérer le véritable compte du cabinet"""
    def get_firm(self, user):
        if hasattr(user, 'collaborator_profile'):
            return user.collaborator_profile.main_account
        return user

class AffairView(BaseFirmView):
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def post(self, request):
        serializer = AffairSerializer(data=request.data)
        if serializer.is_valid():
            # Assigne l'affaire au vrai compte du cabinet et trace le créateur (cabinet ou collaborateur)
            firm = self.get_firm(request.user)
            save_kwargs = {'firm': firm, 'created_by': request.user}
            if hasattr(request.user, 'collaborator_profile') and not serializer.validated_data.get('collaborator'):
                save_kwargs['collaborator'] = request.user.collaborator_profile
            affair = serializer.save(**save_kwargs)

            author_name = get_user_display_name(request.user)
            SiraFolderHistory.objects.create(
                affair_id=affair.id,
                previous_progression=0,
                new_progression=affair.progression,
                action_type="CREATION_DOSSIER",
                document_title=affair.title,
                author=author_name,
                details=f"Création du dossier '{affair.title}' par {author_name}."
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, affair_id=None):
        firm = self.get_firm(request.user)

        if affair_id:
            try:
                # Filtrage unifié basé sur la Firme[cite: 3]
                affair = (
                    Affair.objects
                    .select_related('client', 'firm', 'collaborator', 'created_by')
                    .prefetch_related('documents')
                    .get(id=affair_id, firm=firm, is_deleted=False)
                )
                serializer = AffairSerializer(affair, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Affair.DoesNotExist:
                return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            is_trash = request.query_params.get('trash', 'false').lower() == 'true'
            if is_trash:
                affairs = (
                    Affair.objects
                    .filter(firm=firm, is_deleted=True)
                    .select_related('client', 'firm', 'collaborator', 'created_by')
                    .prefetch_related('documents')
                    .order_by('-deleted_at', '-creation_date')
                )
            else:
                affairs = (
                    Affair.objects
                    .filter(firm=firm, is_archived=False, is_deleted=False)
                    .select_related('client', 'firm', 'collaborator', 'created_by')
                    .prefetch_related('documents')
                )
            client_id = request.query_params.get('client')
            if client_id:
                affairs = affairs.filter(client_id=client_id)
            
            paginator = PageNumberPagination()
            paginator.page_size = 10 
            paginated_affairs = paginator.paginate_queryset(affairs, request)
            serializer = AffairSerializer(paginated_affairs, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

    def patch(self, request, affair_id):
        try:
            firm = self.get_firm(request.user)
            affair = Affair.objects.get(id=affair_id, firm=firm, is_deleted=False)
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
            affair = Affair.objects.get(id=affair_id, firm=firm, is_deleted=False)
            affair.is_deleted = True
            affair.deleted_at = timezone.now()
            affair.save(update_fields=['is_deleted', 'deleted_at'])

            author_name = get_user_display_name(request.user)
            SiraFolderHistory.objects.create(
                affair_id=affair.id,
                previous_progression=affair.progression,
                new_progression=affair.progression,
                action_type="MISE_CORBEILLE_DOSSIER",
                document_title=affair.title,
                author=author_name,
                details=f"Dossier '{affair.title}' déplacé dans la corbeille par {author_name}.",
            )
            return Response({"success": True, "message": "Dossier déplacé vers la corbeille."}, status=status.HTTP_200_OK)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

class ArchivedAffairsView(BaseFirmView):
    """Liste paginée des dossiers archivés du cabinet connecté."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def get(self, request):
        affairs = (
            Affair.objects
            .filter(firm=self.get_firm(request.user), is_archived=True, is_deleted=False)
            .select_related('client', 'firm', 'collaborator', 'created_by')
            .prefetch_related('documents')
        )
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(affairs, request)
        return paginator.get_paginated_response(AffairSerializer(page, many=True, context={'request': request}).data)


class AffairArchiveView(BaseFirmView):
    """Archive un dossier (POST) ou le restaure (DELETE), sans le supprimer."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def post(self, request, affair_id):
        return self._set_archived(request, affair_id, archived=True)

    def delete(self, request, affair_id):
        return self._set_archived(request, affair_id, archived=False)

    def _set_archived(self, request, affair_id, archived):
        try:
            affair = Affair.objects.get(
                id=affair_id,
                firm=self.get_firm(request.user),
            )
        except Affair.DoesNotExist:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        affair.is_archived = archived
        affair.save(update_fields=['is_archived'])
        message = "Dossier archivé avec succès." if archived else "Dossier restauré avec succès."
        return Response({"success": True, "message": message}, status=status.HTTP_200_OK)

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
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]
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

        documents = affair.documents.filter(is_deleted=False)
        paginator = PageNumberPagination()
        paginator.page_size = 12
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100
        paginated_documents = paginator.paginate_queryset(documents, request)
        serializer = DocumentSerializer(paginated_documents, many=True)
        return paginator.get_paginated_response(serializer.data)

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

        category = request.data.get("category")
        serializers = []
        for uploaded_file in files:
            file_name = os.path.basename(uploaded_file.name.replace("\\", "/"))
            title = os.path.splitext(file_name)[0].strip() or file_name
            doc_data = {
                "affair": str(affair.pk),
                "title": title[:200],
                "file": uploaded_file,
            }
            if category:
                doc_data["category"] = category
            serializer = DocumentSerializer(data=doc_data, context={'request': request})
            if not serializer.is_valid():
                return Response(
                    {
                        "error": _extract_first_error(serializer.errors),
                        "files": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializers.append(serializer)

        created_documents = []
        previous = affair.documents.filter(is_deleted=False).order_by("-uploaded_at").first()
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
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            firm = self.get_firm(request.user)
            affair = serializer.validated_data['affair']
            
            # Vérification de sécurité : le dossier appartient-il au cabinet ?
            if affair.firm != firm:
                return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, document_id=None, doc_id=None):
        doc_id = document_id or doc_id
        firm = self.get_firm(request.user)

        if doc_id:
            try:
                document = Document.objects.get(id=doc_id, affair__firm=firm, is_deleted=False)
                serializer = DocumentSerializer(document)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Document.DoesNotExist:
                return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            is_trash = request.query_params.get('trash', 'false').lower() == 'true'
            if is_trash:
                documents = (
                    Document.objects
                    .filter(affair__firm=firm, is_deleted=True)
                    .select_related('affair')
                    .order_by('-deleted_at', '-uploaded_at')
                )
            else:
                documents = (
                    Document.objects
                    .filter(affair__firm=firm, is_deleted=False, affair__is_deleted=False)
                    .select_related('affair')
                )
            affair_id = request.query_params.get('affair')
            if affair_id:
                documents = documents.filter(affair_id=affair_id)

            paginator = PageNumberPagination()
            paginator.page_size = 10 
            paginated_documents = paginator.paginate_queryset(documents, request)
            serializer = DocumentSerializer(paginated_documents, many=True)
            return paginator.get_paginated_response(serializer.data)

    def patch(self, request, document_id=None, doc_id=None):
        doc_id = document_id or doc_id
        if not doc_id:
            return Response({"error": "ID de document requis."}, status=status.HTTP_400_BAD_REQUEST)
        firm = self.get_firm(request.user)
        try:
            document = Document.objects.select_related('affair').get(id=doc_id, affair__firm=firm)
        except Document.DoesNotExist:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        old_affair = document.affair
        target_affair_id = request.data.get('affair')
        target_affair = None
        if target_affair_id and str(target_affair_id) != str(old_affair.id):
            try:
                target_affair = Affair.objects.get(id=target_affair_id, firm=firm)
            except Affair.DoesNotExist:
                return Response(
                    {"error": "Dossier de destination introuvable ou accès refusé."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = DocumentSerializer(document, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            with transaction.atomic():
                if target_affair is not None:
                    # Recoller la chaîne dans l'ancien dossier
                    Document.objects.filter(parent=document).update(parent=document.parent)
                    new_parent = target_affair.documents.order_by('-uploaded_at').first()
                    old_prog = old_affair.progression

                    moved_doc = serializer.save(
                        affair=target_affair,
                        parent=new_parent,
                        relation=Document.Relation.ADDED if new_parent else Document.Relation.INITIAL,
                    )
                    _touch_affair(target_affair)

                    new_old_prog = old_affair.recalculer_progression()
                    author_name = get_user_display_name(request.user)
                    SiraFolderHistory.objects.create(
                        affair_id=old_affair.id,
                        previous_progression=old_prog,
                        new_progression=new_old_prog,
                        action_type="DEPLACEMENT_DOCUMENT",
                        document_title=moved_doc.title,
                        category=moved_doc.category,
                        author=author_name,
                        details=f"Document '{moved_doc.title}' déplacé vers '{target_affair.title}' par {author_name}.",
                    )
                else:
                    serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, document_id=None, doc_id=None):
        doc_id = document_id or doc_id
        if not doc_id:
            return Response({"error": "ID de document requis."}, status=status.HTTP_400_BAD_REQUEST)
        firm = self.get_firm(request.user)
        try:
            document = Document.objects.select_related('affair').get(id=doc_id, affair__firm=firm, is_deleted=False)
        except Document.DoesNotExist:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        affair = document.affair
        old_progression = affair.progression
        author_name = document._resolve_author_name(request.user)

        with transaction.atomic():
            Document.objects.filter(parent=document).update(parent=document.parent)
            document.is_deleted = True
            document.deleted_at = timezone.now()
            document._log_history = False
            document.save(update_fields=['is_deleted', 'deleted_at'])
            new_progression = affair.recalculer_progression()

            SiraFolderHistory.objects.create(
                affair_id=affair.id,
                previous_progression=old_progression,
                new_progression=new_progression,
                action_type="SUPPRESSION_DOCUMENT",
                document_title=document.title,
                category=document.category,
                author=author_name,
                details=f"Document '{document.title}' ({document.category}) déplacé dans la corbeille par {author_name}.",
            )
        return Response({"success": True, "message": "Document déplacé vers la corbeille."}, status=status.HTTP_200_OK)


class RestoreAffairView(BaseFirmView):
    """Restaure un dossier depuis la corbeille."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def post(self, request, affair_id):
        firm = self.get_firm(request.user)
        try:
            affair = Affair.objects.get(id=affair_id, firm=firm, is_deleted=True)
        except Affair.DoesNotExist:
            return Response({"success": False, "message": "Dossier introuvable dans la corbeille."}, status=status.HTTP_404_NOT_FOUND)

        affair.is_deleted = False
        affair.deleted_at = None
        affair.save(update_fields=['is_deleted', 'deleted_at'])

        author_name = get_user_display_name(request.user)
        SiraFolderHistory.objects.create(
            affair_id=affair.id,
            previous_progression=affair.progression,
            new_progression=affair.progression,
            action_type="RESTAURATION_DOSSIER",
            document_title=affair.title,
            author=author_name,
            details=f"Dossier '{affair.title}' restauré depuis la corbeille par {author_name}.",
        )
        return Response({"success": True, "message": "Dossier restauré avec succès.", "dossier": AffairSerializer(affair).data}, status=status.HTTP_200_OK)


class PermanentDeleteAffairView(BaseFirmView):
    """Supprime définitivement un dossier (réservé au compte principal ou admin)."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, affair_id):
        user = request.user
        if not is_firm_admin(user):
            return Response(
                {"success": False, "message": "Action refusée : Seul un administrateur peut supprimer définitivement un dossier."},
                status=status.HTTP_403_FORBIDDEN,
            )

        firm = self.get_firm(user)
        try:
            affair = Affair.objects.get(id=affair_id, firm=firm)
        except Affair.DoesNotExist:
            return Response({"success": False, "message": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        affair.delete()
        return Response({"success": True, "message": "Le dossier a été supprimé définitivement."}, status=status.HTTP_200_OK)


class RestoreDocumentView(BaseFirmView):
    """Restaure un document depuis la corbeille."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def post(self, request, document_id):
        firm = self.get_firm(request.user)
        try:
            document = Document.objects.select_related('affair').get(id=document_id, affair__firm=firm, is_deleted=True)
        except Document.DoesNotExist:
            return Response({"success": False, "message": "Document introuvable dans la corbeille."}, status=status.HTTP_404_NOT_FOUND)

        affair = document.affair
        old_progression = affair.progression
        author_name = document._resolve_author_name(request.user)

        with transaction.atomic():
            document.is_deleted = False
            document.deleted_at = None
            document._log_history = False
            document.save(update_fields=['is_deleted', 'deleted_at'])
            new_progression = affair.recalculer_progression()

            SiraFolderHistory.objects.create(
                affair_id=affair.id,
                previous_progression=old_progression,
                new_progression=new_progression,
                action_type="RESTAURATION_DOCUMENT",
                document_title=document.title,
                category=document.category,
                author=author_name,
                details=f"Document '{document.title}' ({document.category}) restauré depuis la corbeille par {author_name}.",
            )
        return Response({"success": True, "message": "Document restauré avec succès.", "document": DocumentSerializer(document).data}, status=status.HTTP_200_OK)


class PermanentDeleteDocumentView(BaseFirmView):
    """Supprime définitivement un document (réservé au compte principal ou admin)."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, document_id):
        user = request.user
        if not is_firm_admin(user):
            return Response(
                {"success": False, "message": "Action refusée : Seul un administrateur peut supprimer définitivement un document."},
                status=status.HTTP_403_FORBIDDEN,
            )

        firm = self.get_firm(user)
        try:
            document = Document.objects.select_related('affair').get(id=document_id, affair__firm=firm)
        except Document.DoesNotExist:
            return Response({"success": False, "message": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        document.delete(actor=user)
        return Response({"success": True, "message": "Le document a été supprimé définitivement."}, status=status.HTTP_200_OK)


class AffairCommentsView(BaseFirmView):
    """Liste et ajoute des commentaires collaborateurs sur un dossier du cabinet."""
    permission_classes = [IsAuthenticated]

    def _get_affair(self, request, affair_id):
        firm = self.get_firm(request.user)
        try:
            return Affair.objects.get(id=affair_id, firm=firm, is_deleted=False)
        except Affair.DoesNotExist:
            return None

    def get(self, request, affair_id):
        affair = self._get_affair(request, affair_id)
        if not affair:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        comments = (
            affair.comments
            .select_related('author', 'document', 'affair')
            .order_by('created_at')
        )
        doc_id = request.query_params.get('document')
        if doc_id:
            comments = comments.filter(document_id=doc_id)

        serializer = AffairCommentSerializer(comments, many=True, context={'request': request, 'affair': affair})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, affair_id):
        affair = self._get_affair(request, affair_id)
        if not affair:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AffairCommentSerializer(
            data=request.data,
            context={'request': request, 'affair': affair},
        )
        if not serializer.is_valid():
            return Response(
                {"error": _extract_first_error(serializer.errors), **serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            comment = serializer.save(affair=affair, author=request.user)
            _touch_affair(affair)
            AffairCommentRead.objects.update_or_create(
                user=request.user,
                affair=affair,
                defaults={'last_read_at': timezone.now()},
            )
            author_name = get_user_display_name(request.user)
            SiraFolderHistory.objects.create(
                affair_id=affair.id,
                previous_progression=affair.progression,
                new_progression=affair.progression,
                action_type="AJOUT_COMMENTAIRE",
                document_title=comment.document.title if comment.document else affair.title,
                author=author_name,
                details=f"Nouveau commentaire ajouté par {author_name}.",
            )

        out = AffairCommentSerializer(comment, context={'request': request, 'affair': affair})
        return Response(out.data, status=status.HTTP_201_CREATED)


class AffairCommentsUnreadView(BaseFirmView):
    """Retourne le nombre et le dernier aperçu des commentaires non lus d'un dossier pour l'utilisateur courant."""
    permission_classes = [IsAuthenticated]

    def get(self, request, affair_id):
        firm = self.get_firm(request.user)
        try:
            affair = Affair.objects.get(id=affair_id, firm=firm, is_deleted=False)
        except Affair.DoesNotExist:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        qs = affair.comments.select_related('author').exclude(author=request.user)
        read_state = AffairCommentRead.objects.filter(user=request.user, affair=affair).first()
        if read_state:
            qs = qs.filter(created_at__gt=read_state.last_read_at)

        unread_count = qs.count()
        latest = qs.order_by('-created_at').first()
        latest_unread = None
        if latest:
            latest_unread = {
                "id": str(latest.id),
                "author_name": get_user_display_name(latest.author),
                "content": latest.content[:140],
                "created_at": latest.created_at.isoformat(),
            }

        return Response(
            {
                "unread_count": unread_count,
                "total_count": affair.comments.count(),
                "latest_unread": latest_unread,
            },
            status=status.HTTP_200_OK,
        )


class AffairCommentsMarkReadView(BaseFirmView):
    """Marque tous les commentaires d'un dossier comme lus pour l'utilisateur courant."""
    permission_classes = [IsAuthenticated]

    def post(self, request, affair_id):
        firm = self.get_firm(request.user)
        try:
            affair = Affair.objects.get(id=affair_id, firm=firm, is_deleted=False)
        except Affair.DoesNotExist:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        read_state, _ = AffairCommentRead.objects.update_or_create(
            user=request.user,
            affair=affair,
            defaults={'last_read_at': timezone.now()},
        )
        return Response(
            {
                "success": True,
                "unread_count": 0,
                "last_read_at": read_state.last_read_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )


class AffairCommentDetailView(BaseFirmView):
    """Modifie ou supprime un commentaire existant."""
    permission_classes = [IsAuthenticated]

    def _get_comment(self, request, comment_id):
        firm = self.get_firm(request.user)
        try:
            return AffairComment.objects.select_related('affair', 'author', 'document').get(
                id=comment_id,
                affair__firm=firm,
                affair__is_deleted=False,
            )
        except AffairComment.DoesNotExist:
            return None

    def patch(self, request, comment_id):
        comment = self._get_comment(request, comment_id)
        if not comment:
            return Response({"error": "Commentaire introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if comment.author_id != request.user.id:
            return Response(
                {"error": "Seul l'auteur du commentaire peut le modifier."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AffairCommentSerializer(
            comment,
            data={"content": request.data.get("content", "")},
            partial=True,
            context={'request': request, 'affair': comment.affair},
        )
        if not serializer.is_valid():
            return Response(
                {"error": _extract_first_error(serializer.errors), **serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = serializer.save(is_edited=True)
        out = AffairCommentSerializer(updated, context={'request': request, 'affair': comment.affair})
        return Response(out.data, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        comment = self._get_comment(request, comment_id)
        if not comment:
            return Response({"error": "Commentaire introuvable."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_author = comment.author_id == user.id
        is_firm_owner = comment.affair.firm_id == user.id
        is_firm_admin = (
            hasattr(user, 'collaborator_profile')
            and user.collaborator_profile.main_account_id == comment.affair.firm_id
            and user.collaborator_profile.role == 'admin'
        )

        if not (is_author or is_firm_owner or is_firm_admin):
            return Response(
                {"error": "Vous n'êtes pas autorisé à supprimer ce commentaire."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        return Response({"success": True, "message": "Commentaire supprimé."}, status=status.HTTP_200_OK)


class DocumentDownloadView(BaseFirmView):
    """Téléchargement / aperçu authentifié d'un document du cabinet."""
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        firm = self.get_firm(request.user)
        try:
            document = Document.objects.select_related('affair').get(id=document_id, affair__firm=firm)
        except Document.DoesNotExist:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        file_path = resolve_document_file_path(document)
        if not file_path:
            return Response({"error": "Fichier introuvable sur le serveur."}, status=status.HTTP_404_NOT_FOUND)

        ext = os.path.splitext(file_path)[1].lower()
        guessed_type, _ = mimetypes.guess_type(file_path)
        content_type = DOCUMENT_MIME_TYPES.get(ext) or guessed_type or 'application/octet-stream'

        return FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=False,
            filename=os.path.basename(file_path),
        )


def _get_document_version_chain(doc):
    """Retourne la lignée chronologique complète (v1 -> ... -> latest) d'un document."""
    visited = set()
    root = doc
    while root.relation == Document.Relation.UPDATED and root.parent_id and root.parent_id not in visited:
        visited.add(root.pk)
        parent = Document.objects.filter(pk=root.parent_id, affair_id=doc.affair_id, is_deleted=False).first()
        if not parent:
            break
        root = parent

    chain = [root]
    seen_ids = {root.pk}
    queue = [root]
    while queue:
        current = queue.pop(0)
        children = Document.objects.filter(
            parent_id=current.pk,
            affair_id=doc.affair_id,
            relation=Document.Relation.UPDATED,
            is_deleted=False,
        ).order_by('version', 'uploaded_at')
        for child in children:
            if child.pk not in seen_ids:
                seen_ids.add(child.pk)
                chain.append(child)
                queue.append(child)

    chain.sort(key=lambda item: (item.version or 1, item.uploaded_at))
    return chain


class DocumentVersionView(BaseFirmView):
    """Liste l'historique des versions d'un document et ajoute une nouvelle version (v+1)."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, document_id):
        firm = self.get_firm(request.user)
        try:
            base_doc = Document.objects.select_related('affair').get(
                id=document_id,
                affair__firm=firm,
                is_deleted=False,
            )
        except Document.DoesNotExist:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        chain = _get_document_version_chain(base_doc)
        versions = list(reversed(chain))

        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100
        page = paginator.paginate_queryset(versions, request)
        serializer = DocumentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, document_id):
        firm = self.get_firm(request.user)
        try:
            base_doc = Document.objects.select_related('affair').get(
                id=document_id,
                affair__firm=firm,
                is_deleted=False,
            )
        except Document.DoesNotExist:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"error": "Veuillez sélectionner un fichier.", "file": "Veuillez sélectionner un fichier."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chain = _get_document_version_chain(base_doc)
        latest_doc = chain[-1]

        doc_data = {
            "affair": str(latest_doc.affair_id),
            "title": (request.data.get("title") or latest_doc.title)[:200],
            "file": uploaded_file,
            "category": request.data.get("category") or latest_doc.category,
            "version_note": (request.data.get("version_note") or "")[:300],
        }
        for coord in ("pos_x", "pos_y"):
            raw_val = request.data.get(coord)
            if raw_val not in (None, ""):
                try:
                    doc_data[coord] = float(raw_val)
                except (TypeError, ValueError):
                    pass

        serializer = DocumentSerializer(data=doc_data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {
                    "error": _extract_first_error(serializer.errors),
                    **serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            new_doc = serializer.save(
                parent=latest_doc,
                relation=Document.Relation.UPDATED,
                version=(latest_doc.version or 1) + 1,
                uploaded_by=request.user,
                updated_by=request.user,
            )
            _touch_affair(latest_doc.affair)

        return Response(DocumentSerializer(new_doc).data, status=status.HTTP_201_CREATED)


class DocumentVersionRestoreView(BaseFirmView):
    """Restaure une ancienne version d'un document en créant une nouvelle version (façon Git)."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def post(self, request, document_id):
        firm = self.get_firm(request.user)
        try:
            target_doc = Document.objects.select_related('affair').get(
                id=document_id,
                affair__firm=firm,
                is_deleted=False,
            )
        except Document.DoesNotExist:
            return Response({"error": "Version introuvable."}, status=status.HTTP_404_NOT_FOUND)

        file_path = resolve_document_file_path(target_doc)
        if not file_path:
            return Response(
                {"error": "Le fichier physique de cette version est introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        chain = _get_document_version_chain(target_doc)
        latest_doc = chain[-1]
        note = (request.data.get("version_note") or f"Restauré depuis la v{target_doc.version}").strip()[:300]
        base_filename = os.path.basename(file_path)

        with open(file_path, "rb") as fh:
            raw_bytes = fh.read()

        with transaction.atomic():
            restored_doc = Document(
                affair=latest_doc.affair,
                title=latest_doc.title,
                category=latest_doc.category,
                parent=latest_doc,
                relation=Document.Relation.UPDATED,
                version=(latest_doc.version or 1) + 1,
                version_note=note,
                uploaded_by=request.user,
                updated_by=request.user,
                pos_x=latest_doc.pos_x,
                pos_y=latest_doc.pos_y,
            )
            restored_doc._actor = request.user
            restored_doc.file.save(base_filename, ContentFile(raw_bytes), save=False)
            restored_doc.save()
            _touch_affair(latest_doc.affair)

        return Response(DocumentSerializer(restored_doc).data, status=status.HTTP_201_CREATED)


class DocumentShareLinkView(BaseFirmView):
    """Liste, crée et révoque les liens de partage publics d'un document."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def _get_document(self, request, document_id):
        firm = self.get_firm(request.user)
        try:
            return Document.objects.select_related('affair').get(id=document_id, affair__firm=firm)
        except Document.DoesNotExist:
            return None

    def get(self, request, document_id):
        document = self._get_document(request, document_id)
        if not document:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        links = document.share_links.filter(is_active=True)
        serializer = DocumentShareLinkSerializer(links, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, document_id):
        document = self._get_document(request, document_id)
        if not document:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        expires_in_days = request.data.get("expires_in_days", 7)
        expires_at = None
        if expires_in_days not in (None, "", 0, "0"):
            try:
                days = int(expires_in_days)
                if days > 0:
                    expires_at = timezone.now() + timedelta(days=days)
            except (TypeError, ValueError):
                return Response(
                    {"error": "Durée d'expiration invalide."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        link = DocumentShareLink.objects.create(
            document=document,
            created_by=request.user,
            expires_at=expires_at,
        )
        serializer = DocumentShareLinkSerializer(link, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, document_id, link_id=None):
        document = self._get_document(request, document_id)
        if not document:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if not link_id:
            return Response({"error": "ID du lien requis."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = DocumentShareLink.objects.filter(id=link_id, document=document).delete()
        if not deleted_count:
            return Response({"error": "Lien introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Lien révoqué avec succès."}, status=status.HTTP_204_NO_CONTENT)


class PublicDocumentShareView(APIView):
    """Accès public (sans connexion) à un document via son lien de partage."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        try:
            link = DocumentShareLink.objects.select_related('document', 'document__affair').get(token=token)
        except DocumentShareLink.DoesNotExist:
            return Response({"error": "Lien de partage invalide ou introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if not link.is_valid:
            return Response({"error": "Ce lien de partage a expiré ou a été révoqué."}, status=status.HTTP_410_GONE)

        file_path = resolve_document_file_path(link.document)
        if not file_path:
            return Response({"error": "Fichier introuvable sur le serveur."}, status=status.HTTP_404_NOT_FOUND)

        DocumentShareLink.objects.filter(pk=link.pk).update(download_count=F('download_count') + 1)

        ext = os.path.splitext(file_path)[1].lower()
        guessed_type, _ = mimetypes.guess_type(file_path)
        content_type = DOCUMENT_MIME_TYPES.get(ext) or guessed_type or 'application/octet-stream'

        return FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=False,
            filename=os.path.basename(file_path),
        )


class AffairShareLinkView(BaseFirmView):
    """Liste, crée et révoque les liens de partage publics d'un dossier (affaire)."""
    permission_classes = [IsAuthenticated, IsFirmEditorOrReadOnly]

    def _get_affair(self, request, affair_id):
        firm = self.get_firm(request.user)
        try:
            return Affair.objects.get(id=affair_id, firm=firm)
        except Affair.DoesNotExist:
            return None

    def get(self, request, affair_id):
        affair = self._get_affair(request, affair_id)
        if not affair:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        links = affair.share_links.filter(is_active=True)
        serializer = AffairShareLinkSerializer(links, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, affair_id):
        affair = self._get_affair(request, affair_id)
        if not affair:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        expires_in_days = request.data.get("expires_in_days", 7)
        expires_at = None
        if expires_in_days not in (None, "", 0, "0"):
            try:
                days = int(expires_in_days)
                if days > 0:
                    expires_at = timezone.now() + timedelta(days=days)
            except (TypeError, ValueError):
                return Response(
                    {"error": "Durée d'expiration invalide."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        link = AffairShareLink.objects.create(
            affair=affair,
            created_by=request.user,
            expires_at=expires_at,
        )
        serializer = AffairShareLinkSerializer(link, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, affair_id, link_id=None):
        affair = self._get_affair(request, affair_id)
        if not affair:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if not link_id:
            return Response({"error": "ID du lien requis."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = AffairShareLink.objects.filter(id=link_id, affair=affair).delete()
        if not deleted_count:
            return Response({"error": "Lien introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Lien révoqué avec succès."}, status=status.HTTP_204_NO_CONTENT)


class PublicAffairShareView(APIView):
    """Accès public (sans connexion) à un dossier via son lien : téléchargement en archive ZIP."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        try:
            link = AffairShareLink.objects.select_related('affair').get(token=token)
        except AffairShareLink.DoesNotExist:
            return Response({"error": "Lien de partage invalide ou introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if not link.is_valid:
            return Response({"error": "Ce lien de partage a expiré ou a été révoqué."}, status=status.HTTP_410_GONE)

        docs = list(link.affair.documents.all())
        buffer = io.BytesIO()
        added_files = 0
        used_names = set()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for doc in docs:
                file_path = resolve_document_file_path(doc)
                if not file_path:
                    continue
                base_name = os.path.basename(file_path)
                arcname = base_name
                counter = 1
                stem, ext = os.path.splitext(base_name)
                while arcname.lower() in used_names:
                    arcname = f"{stem}_{counter}{ext}"
                    counter += 1
                used_names.add(arcname.lower())
                zf.write(file_path, arcname=arcname)
                added_files += 1

        if added_files == 0:
            return Response(
                {"error": "Ce dossier ne contient aucun document téléchargeable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        AffairShareLink.objects.filter(pk=link.pk).update(download_count=F('download_count') + 1)
        buffer.seek(0)
        safe_ref = (link.affair.reference_affair or "dossier").replace("/", "_").replace("\\", "_")
        return FileResponse(
            buffer,
            content_type='application/zip',
            as_attachment=True,
            filename=f"{safe_ref}.zip",
        )