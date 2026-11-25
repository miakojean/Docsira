from rest_framework import serializers
from .models import CustomUser, Collaborator, CollaboratorInvitation, ActivationCode
from .permissions import can_edit_firm, get_user_role, is_firm_admin

# 1. NOUVEAU : Un sérialiseur allégé pour l'affichage imbriqué
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # On ne renvoie que les données strictement nécessaires au frontend
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

# 2. CORRECTION : Sécurisation du sérialiseur principal
class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_firm_owner = serializers.SerializerMethodField()
    can_manage_collaborators = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'account_type',
            'has_changed_password',
            'role',
            'is_firm_owner',
            'can_manage_collaborators',
            'can_edit',
            'password',
        ]
        read_only_fields = ['role', 'is_firm_owner', 'can_manage_collaborators', 'can_edit']
        # On rend le mot de passe invisible en lecture !
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_role(self, obj):
        return get_user_role(obj)

    def get_is_firm_owner(self, obj):
        return get_user_role(obj) == 'owner'

    def get_can_manage_collaborators(self, obj):
        return is_firm_admin(obj)

    def get_can_edit(self, obj):
        return can_edit_firm(obj)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

# 3. MISE À JOUR : Utilisation du sérialiseur allégé
class CollaboratorSerializer(serializers.ModelSerializer):
    # On remplace CustomUserSerializer par SimpleUserSerializer
    user = SimpleUserSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Collaborator
        fields = [
            'id',
            'main_account',
            'role',
            'user',
            'email',
            'status',
            'created_at'
        ]
        read_only_fields = ['main_account']

    def get_status(self, obj):
        if obj.user.has_usable_password():
            return 'accepted'
        return 'pending'


class CollaboratorInvitationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CollaboratorInvitation
        fields = [
            'id', 
            'main_account', 
            'email', 
            'role', 
            'created_at'
        ]
        read_only_fields = fields

class ActivationCodeSerializer(serializers.ModelSerializer):
    # On remplace CustomUserSerializer par SimpleUserSerializer ici aussi
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = ActivationCode
        fields = [
            'id',
            'user',
            'code',
            'is_used',
            'created_at',
            'updated_at',
            'expires_at'
        ]
        read_only_fields = ['id']
