from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import uuid

class CustomUser(AbstractUser):
    # Les types de comptes principaux

    class AccountType(models.TextChoices):
        FIRM = "firm", _("Firm")
        INDIVIDUAL = "individual", _("Individual")
        COLLABORATOR = "collaborator", _("Collaborator") # Optionnel : pour différencier les comptes invités

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.FIRM,
        verbose_name=_("Type de compte")
    )

    def __str__(self):
        return self.username


class Collaborator(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # 1. Le compte principal (Firme ou Individu) qui a ajouté le collaborateur
    main_account = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='hired_collaborators',
        verbose_name=_("Compte Principal")
    )

    # 2. Le compte utilisateur du collaborateur lui-même
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='collaborator_profile',
        verbose_name=_("Utilisateur")
    )

    # 3. La responsabilité / Le rôle (qui correspond à ton front-end Vue.js)
    class Roles(models.TextChoices):
        VIEWER = "viewer", _("Lecteur")
        EDITOR = "editor", _("Éditeur")
        ADMIN = "admin", _("Administrateur")

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.VIEWER,
        verbose_name=_("Responsabilité")
    )

    # Date d'ajout pour l'historique (toujours utile)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un utilisateur ne peut être le collaborateur d'un même compte principal qu'une seule fois
        unique_together = ('main_account', 'user')
        verbose_name = _("Collaborateur")
        verbose_name_plural = _("Collaborateurs")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) chez {self.main_account.username}"


class CollaboratorInvitation(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    main_account = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='collaborator_invitations',
        verbose_name=_("Compte Principal")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_collaborator_invitations',
        verbose_name=_("Utilisateur invité")
    )
    role = models.CharField(
        max_length=20,
        choices=Collaborator.Roles.choices,
        default=Collaborator.Roles.VIEWER,
        verbose_name=_("Responsabilité")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('main_account', 'user'),
                name='unique_collaborator_invitation'
            )
        ]

    def __str__(self):
        return f"Invitation pour {self.user.email} chez {self.main_account.username}"

class ActivationCode(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activation_codes')
    code = models.CharField(max_length=6, unique=True)
    is_used = models.BooleanField(default=False)
    # Timestamp pour savoir quand le code a été généré
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    expires_at = models.DateTimeField()

    @classmethod
    def create_code(cls, user, expiration_hours=24):
        code = cls(
            user = user,
            expires_at = timezone.now() + timedelta(hours=expiration_hours)
        )
        code.save()
        return code

    def __str__(self):
        return f"Activation code for {self.user.username}"