from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_user_firm(user):
    """Retourne le compte principal du cabinet auquel l'utilisateur appartient."""
    if not user or not user.is_authenticated:
        return None
    if hasattr(user, 'collaborator_profile'):
        return user.collaborator_profile.main_account
    return user


def get_user_role(user):
    """Retourne le rôle effectif : owner, admin, editor (Collaborateur) ou viewer (Lecteur)."""
    if not user or not user.is_authenticated:
        return 'viewer'
    if hasattr(user, 'collaborator_profile'):
        return user.collaborator_profile.role or 'editor'
    return 'owner'


def is_firm_admin(user):
    """Vrai pour le propriétaire du cabinet et les collaborateurs ayant le rôle admin."""
    return get_user_role(user) in ('owner', 'admin')


def can_edit_firm(user):
    """Vrai pour les utilisateurs pouvant créer/modifier/partager (owner, admin, editor)."""
    return get_user_role(user) in ('owner', 'admin', 'editor')


class IsFirmEditorOrReadOnly(BasePermission):
    """Autorise la lecture à tous les membres du cabinet, mais bloque les écritures pour les Lecteurs (viewer)."""

    message = (
        "Votre rôle Lecteur ne permet pas de modifier ce contenu. "
        "Vous pouvez consulter les documents et laisser des commentaires."
    )

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return can_edit_firm(request.user)


class IsFirmAdmin(BasePermission):
    """Autorise uniquement le propriétaire du cabinet ou un collaborateur administrateur."""

    message = "Action réservée aux administrateurs du cabinet."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_firm_admin(request.user))

