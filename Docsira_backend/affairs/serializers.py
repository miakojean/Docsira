from rest_framework import serializers
from .models import Affair
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

    class Meta:
        model = Affair
        fields = '__all__'
        # On empêche formellement l'écrasement de ces champs système[cite: 2, 3]
        read_only_fields = ['reference_affair', 'path_affair', 'firm']