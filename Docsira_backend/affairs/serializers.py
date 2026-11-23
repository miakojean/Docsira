import os
from rest_framework import serializers
from .models import (
    ALLOWED_DOCUMENT_EXTENSIONS,
    Affair,
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

    def get_created_by_name(self, obj):
        if obj.created_by:
            return get_user_display_name(obj.created_by)
        if obj.collaborator:
            return get_user_display_name(obj.collaborator.user)
        if obj.firm:
            return get_user_display_name(obj.firm)
        return "Système"

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_documents_preview(self, obj):
        """Extensions (max 3) des derniers documents, pour l'aperçu du dossier."""
        docs = obj.documents.order_by('-uploaded_at')[:3]
        return [
            os.path.splitext(d.file.name)[1].lstrip('.').lower() if d.file else ''
            for d in docs
        ]

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
    file = serializers.FileField(required=False)

    class Meta:
        model = Document
        fields = ['id', 'affair', 'title', 'file', 'file_name', 'extension', 'size',
                  'download_url', 'uploaded_at', 'parent', 'relation', 'version',
                  'category', 'valide', 'pos_x', 'pos_y']
        read_only_fields = ['file_name', 'extension', 'size', 'download_url',
                            'parent', 'relation', 'version']

    def create(self, validated_data):
        request = self.context.get('request')
        instance = Document(**validated_data)
        if request and request.user and request.user.is_authenticated:
            instance._actor = request.user
        instance.save()
        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request')
        meaningful_fields = set(validated_data.keys()) - {'pos_x', 'pos_y'}
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if request and request.user and request.user.is_authenticated:
            instance._actor = request.user
        instance._log_history = bool(meaningful_fields)
        instance.save()
        return instance

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