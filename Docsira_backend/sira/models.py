# sira/models.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class SiraCategory(models.TextChoices):
    IDENTIFICATION = 'IDENTIFICATION', _('Identification (45%)')
    CONSTITUTION = 'CONSTITUTION', _('Constitution (60%)')
    PROCEDURES = 'PROCEDURES', _('Procédures (75%)')
    LIVRABLES = 'LIVRABLES', _('Livrables (90%)')
    CLOTURE = 'CLOTURE', _('Clôture (100%)')

class SiraProgressRules:
    """Règles métier fixes pour les pourcentages SIRA"""
    THRESHOLDS = {
        'IDENTIFICATION': 45,
        'CONSTITUTION': 60,
        'PROCEDURES': 75,
        'LIVRABLES': 90,
        'CLOTURE': 100,
    }


class SiraFolderHistory(models.Model):
    """
    Module indépendant de versionnage et d'historique des dossiers.
    Enregistre l'état du dossier à chaque modification de document.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Lien générique ou ciblé vers votre modèle Affair existant
    affair_id = models.UUIDField(_("ID de l'Affaire"), db_index=True)
    
    # Données instantanées de l'historique (Snapshot)
    previous_progression = models.PositiveSmallIntegerField(_("Ancienne progression"))
    new_progression = models.PositiveSmallIntegerField(_("Nouvelle progression"))
    action_type = models.CharField(_("Type d'action"), max_length=50) # AJOUT, SUPPRESSION, VALIDATION
    document_title = models.CharField(_("Document concerné"), max_length=200, blank=True, null=True)
    category = models.CharField(_("Catégorie SIRA"), max_length=30, choices=SiraCategory.choices, blank=True, null=True)
    
    # Traçabilité
    author = models.CharField(_("Auteur de l'action"), max_length=150, blank=True, null=True)
    timestamp = models.DateTimeField(_("Date et heure de l'historique"), auto_now_add=True)
    details = models.TextField(_("Détails de la transition"), blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Historique SIRA du dossier")
        verbose_name_plural = _("Historiques SIRA des dossiers")

    def __str__(self):
        return f"Dossier {self.affair_id} -> {self.new_progression}% ({self.timestamp.strftime('%d/%m/%Y %H:%M')})"