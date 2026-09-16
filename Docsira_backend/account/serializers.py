from rest_framework import serializers
from .models import CustomUser, Collaborator

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'account_type',
            'password',
        ]

    def create(self, validated_data):

        user = CustomUser.objects.create_user(**validated_data,)
        return user

class CollaboratorSerializer(serializers.ModelSerializer):
    # 1. LECTURE : On utilise le CustomUserSerializer pour afficher les infos complètes
    # (On utilise 'user' car c'est le nom exact du champ dans ton modèle Collaborator)
    user = CustomUserSerializer(read_only=True)

    # 2. ÉCRITURE : On ajoute un champ virtuel pour capter l'email envoyé par ton front-end Vue.js
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Collaborator
        fields = [
            'id',
            'main_account',
            'role',
            'user',
            'email', # Champ virtuel utilisé uniquement à la création
            'created_at'
        ]
        # Le main_account sera injecté automatiquement par la vue, pas par le frontend
        read_only_fields = ['main_account']
