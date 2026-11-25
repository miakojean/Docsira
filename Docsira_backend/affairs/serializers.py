import os
from rest_framework import serializers
from .models import (
    ALLOWED_DOCUMENT_EXTENSIONS,
    Affair,
    AffairComment,
    AffairCommentRead,
    AffairShareLink,
    Document,
    DocumentShareLink,
    get_user_display_name,
    resolve_document_file_path,
)
from Client.models import Client
from account.models import Collaborator

# Imports de tes serializers existants
from account.serializers import CustomUserSerializer, CollaboratorSerializer
from Client.serializers import ClientSerializer

class AffairSerializer(serializers.ModelSerializer):
    # 1. ÉCRITURE : Champs virtuels pour intercepter les UUID envoyés via le POST[cite: 1, 3]
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source='client', write_only=True, required=False
    )
    collaborator_id = serializers.PrimaryKeyRelatedField(
        queryset=Collaborator.objects.all(), source='collaborator', write_only=True,
        required=False, allow_null=True
    )

    # 2. LECTURE : Champs imbriqués pour l'affichage Frontend[cite: 3]
    # Idéalement, utilise ton SimpleUserSerializer pour 'firm' afin d'être encore plus léger !
    firm = CustomUserSerializer(read_only=True) 
    created_by = CustomUserSerializer(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    collaborator = CollaboratorSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    documents_count = serializers.SerializerMethodField()
    documents_preview = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    unread_comments_count = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return get_user_display_name(obj.created_by)
        if obj.collaborator:
            return get_user_display_name(obj.collaborator.user)
        if obj.firm:
            return get_user_display_name(obj.firm)
        return "Système"

    def get_documents_count(self, obj):
        return obj.documents.filter(is_deleted=False).count()

    def get_documents_preview(self, obj):
        """Extensions (max 3) des derniers documents, pour l'aperçu du dossier."""
        docs = obj.documents.filter(is_deleted=False).order_by('-uploaded_at')[:3]
        return [
            os.path.splitext(d.file.name)[1].lstrip('.').lower() if d.file else ''
            for d in docs
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_unread_comments_count(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return 0
        qs = obj.comments.exclude(author=user)
        read_state = AffairCommentRead.objects.filter(user=user, affair=obj).first()
        if read_state:
            qs = qs.filter(created_at__gt=read_state.last_read_at)
        return qs.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # S'assure que la progression SIRA est toujours calculée dynamiquement et à jour
        sira_prog = instance.calculer_progression_sira()
        data['progression'] = sira_prog
        if instance.progression != sira_prog:
            Affair.objects.filter(pk=instance.pk).update(progression=sira_prog)
            instance.progression = sira_prog
        return data

    class Meta:
        model = Affair
        fields = '__all__'
        # On empêche formellement l'écrasement de ces champs système[cite: 2, 3]
        read_only_fields = ['reference_affair', 'path_affair', 'firm', 'created_by']

class DocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    affair_title = serializers.CharField(source='affair.title', read_only=True)
    affair_reference = serializers.CharField(source='affair.reference_affair', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    file = serializers.FileField(required=False)

    class Meta:
        model = Document
        fields = ['id', 'affair', 'affair_title', 'affair_reference', 'title', 'file',
                  'file_name', 'extension', 'size', 'download_url', 'uploaded_at', 'updated_at',
                  'parent', 'relation', 'version', 'version_note', 'uploaded_by_name',
                  'created_by_name', 'updated_by_name',
                  'category', 'valide', 'pos_x', 'pos_y',
                  'is_deleted', 'deleted_at']
        read_only_fields = ['file_name', 'extension', 'size', 'download_url',
                            'affair_title', 'affair_reference', 'uploaded_by_name',
                            'created_by_name', 'updated_by_name', 'updated_at',
                            'parent', 'relation', 'version', 'is_deleted', 'deleted_at']

    def create(self, validated_data):
        request = self.context.get('request')
        instance = Document(**validated_data)
        if request and request.user and request.user.is_authenticated:
            instance.uploaded_by = request.user
            instance._actor = request.user
        instance.save()
        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request')
        meaningful_fields = set(validated_data.keys()) - {'pos_x', 'pos_y'}
        old_valide = instance.valide
        old_category = instance.category
        old_title = instance.title

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        actor = request.user if (request and request.user and request.user.is_authenticated) else None
        if actor is not None:
            instance._actor = actor
            if meaningful_fields:
                instance.updated_by = actor
        actor_label = instance._resolve_author_name(actor)

        if 'valide' in validated_data and validated_data['valide'] != old_valide:
            instance._history_action = 'VALIDATION_DOCUMENT'
            state_label = 'validé' if instance.valide else 'validation retirée'
            instance._history_details = f"Document '{instance.title}' {state_label} par {actor_label}."
        elif 'category' in validated_data and validated_data['category'] != old_category:
            instance._history_action = 'CHANGEMENT_CATEGORIE'
            instance._history_details = (
                f"Catégorie SIRA de '{instance.title}' modifiée ({old_category} → {instance.category}) par {actor_label}."
            )
        elif 'title' in validated_data and validated_data['title'] != old_title:
            instance._history_action = 'RENOMMAGE_DOCUMENT'
            instance._history_details = f"Document renommé '{old_title}' → '{instance.title}' par {actor_label}."

        instance._log_history = bool(meaningful_fields)
        instance.save()
        return instance

    def get_uploaded_by_name(self, obj):
        return get_user_display_name(obj.uploaded_by) if obj.uploaded_by else None

    def get_created_by_name(self, obj):
        curr = obj
        visited = {curr.pk}
        while (
            curr.relation == Document.Relation.UPDATED
            and curr.parent_id
            and curr.parent_id not in visited
        ):
            parent = curr.parent
            if not parent:
                break
            visited.add(parent.pk)
            curr = parent
        creator = (
            curr.uploaded_by
            or obj.uploaded_by
            or (obj.affair.created_by if obj.affair_id else None)
        )
        return get_user_display_name(creator) if creator else None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return get_user_display_name(obj.updated_by)
        if obj.relation == Document.Relation.UPDATED and obj.uploaded_by:
            return get_user_display_name(obj.uploaded_by)
        return None

    def validate_file(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
                raise serializers.ValidationError(
                    "Format de fichier non autorisé. Seuls les documents PDF (.pdf), Word (.doc, .docx) et images (.png, .jpg, .jpeg, .webp, .gif) sont acceptés."
                )
        return value

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else ''

    def get_extension(self, obj):
        return os.path.splitext(obj.file.name)[1].lstrip('.').lower() if obj.file else ''

    def get_size(self, obj):
        try:
            return obj.file.size
        except (OSError, ValueError):
            file_path = resolve_document_file_path(obj)
            if file_path:
                try:
                    return os.path.getsize(file_path)
                except OSError:
                    return 0
            return 0  # fichier manquant sur le disque

    def get_download_url(self, obj):
        return f"/affairs/documents/{obj.id}/download/"


class DocumentShareLinkSerializer(serializers.ModelSerializer):
    share_url = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = DocumentShareLink
        fields = [
            'id',
            'document',
            'token',
            'share_url',
            'created_at',
            'expires_at',
            'is_active',
            'is_expired',
            'download_count',
        ]
        read_only_fields = ['id', 'document', 'token', 'share_url', 'created_at', 'is_expired', 'download_count']

    def get_share_url(self, obj):
        path = f"/affairs/share/{obj.token}/"
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(path)
        return path


class AffairShareLinkSerializer(serializers.ModelSerializer):
    share_url = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = AffairShareLink
        fields = [
            'id',
            'affair',
            'token',
            'share_url',
            'created_at',
            'expires_at',
            'is_active',
            'is_expired',
            'download_count',
        ]
        read_only_fields = ['id', 'affair', 'token', 'share_url', 'created_at', 'is_expired', 'download_count']

    def get_share_url(self, obj):
        path = f"/affairs/share/dossier/{obj.token}/"
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(path)
        return path


class AffairCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_initials = serializers.SerializerMethodField()
    document_title = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = AffairComment
        fields = [
            'id',
            'affair',
            'document',
            'document_title',
            'parent',
            'author',
            'author_name',
            'author_initials',
            'content',
            'is_edited',
            'created_at',
            'updated_at',
            'can_edit',
            'can_delete',
        ]
        read_only_fields = [
            'id',
            'affair',
            'author',
            'author_name',
            'author_initials',
            'document_title',
            'is_edited',
            'created_at',
            'updated_at',
            'can_edit',
            'can_delete',
        ]

    def get_author_name(self, obj):
        user = obj.author
        if not user:
            return "Utilisateur"
        full_name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        return full_name or user.username or user.email or "Utilisateur"

    def get_author_initials(self, obj):
        name = self.get_author_name(obj)
        parts = [p for p in name.split() if p]
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return name[:2].upper() if name else "U"

    def get_document_title(self, obj):
        if obj.document and not obj.document.is_deleted:
            return obj.document.title or os.path.basename(obj.document.file.name)
        return None

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.author_id == request.user.id

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        if obj.author_id == user.id or obj.affair.firm_id == user.id:
            return True
        if hasattr(user, 'collaborator_profile'):
            collab = user.collaborator_profile
            if collab.main_account_id == obj.affair.firm_id and collab.role == 'admin':
                return True
        return False

    def validate_content(self, value):
        cleaned = (value or '').strip()
        if not cleaned:
            raise serializers.ValidationError("Le commentaire ne peut pas être vide.")
        if len(cleaned) > 4000:
            raise serializers.ValidationError("Le commentaire ne peut pas dépasser 4000 caractères.")
        return cleaned

    def validate(self, attrs):
        affair = self.context.get('affair') or (self.instance.affair if self.instance else None)
        document = attrs.get('document')
        parent = attrs.get('parent')

        if affair and document and (document.affair_id != affair.id or document.is_deleted):
            raise serializers.ValidationError({"document": "Ce document n'appartient pas à ce dossier."})

        if affair and parent:
            if parent.affair_id != affair.id:
                raise serializers.ValidationError({"parent": "Le commentaire parent n'appartient pas à ce dossier."})
            # Limiter l'imbrication à 1 niveau de réponses pour garder la discussion lisible
            if parent.parent_id is not None:
                attrs['parent'] = parent.parent

        return attrs