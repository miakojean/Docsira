from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    # Les types de comptes principaux
    class AccountType(models.TextChoices):
        FIRM = "firm", _("Firm")
        INDIVIDUAL = "individual", _("Individual")
        COLLABORATOR = "collaborator", _("Collaborator") # Optionnel : pour différencier les comptes invités

    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.FIRM,
        verbose_name=_("Type de compte")
    )

    def __str__(self):
        return self.username


class Collaborator(models.Model):
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
