import os
from rest_framework import serializers
from .models import Affair, Document
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
    collaborator = CollaboratorSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    documents_count = serializers.SerializerMethodField()

    def get_documents_count(self, obj):
        return obj.documents.count()

    class Meta:
        model = Affair
        fields = '__all__'
        # On empêche formellement l'écrasement de ces champs système[cite: 2, 3]
        read_only_fields = ['reference_affair', 'path_affair', 'firm']

class DocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'affair', 'title', 'file', 'file_name', 'extension', 'size',
                  'download_url', 'uploaded_at', 'parent', 'relation', 'version',
                  'pos_x', 'pos_y']
        read_only_fields = ['file_name', 'extension', 'size', 'download_url',
                            'parent', 'relation', 'version']

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else ''

    def get_extension(self, obj):
        return os.path.splitext(obj.file.name)[1].lstrip('.').lower() if obj.file else ''

    def get_size(self, obj):
        try:
            return obj.file.size
        except (OSError, ValueError):
            return 0  # fichier manquant sur le disque

    def get_download_url(self, obj):
        return f"/affairs/documents/{obj.id}/download/"

    def __str__(self):
        return f"{self.title} ({self.affair.reference_affair})"