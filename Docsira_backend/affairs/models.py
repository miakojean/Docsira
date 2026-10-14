import os
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# Relation 
from account.models import CustomUser, Collaborator
from Client.models import Client
# Create your models here.

class Affair(models.Model):

    TYPE_DOSSIER_CHOICES = [
        ('CONSTITUTION', 'Constitution de société'),
        ('MODIFICATION', 'Modification statutaire'),
        ('DISSOLUTION', 'Dissolution/Liquidation'),
        ('CONTENTIEUX', 'Contentieux'),
        ('CONSEIL', 'Conseil juridique'),
        ('CONTRAT', 'Rédaction de contrat'),
        ('AUDIT', 'Audit juridique'),
        ('PROPRIETE_INTELLECTUELLE', 'Propriété intellectuelle'),
        ('FUSION_ACQUISITION', 'Fusion/Acquisition'),
        ('RECOUVREMENT', 'Recouvrement de créances'),
        ('AUTRE', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('NOUVEAU', 'Nouveau'),
        ('EN_COURS', 'En cours'),
        ('EN_ATTENTE', 'En attente (client)'),
        ('BLOQUE', 'Bloqué'),
        ('TERMINE', 'Terminé'),
        ('CLOTURE', 'Clôturé'),
        ('ANNULE', 'Annulé'),
    ]

    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('URGENTE', 'Urgente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Utilisation d'un UUID pour l'identifiant unique

    # Identification
    reference_affair = models.CharField(_("Référence dossier"), max_length=50, unique=True, editable=False)
    title = models.CharField(_("Titre du dossier"), max_length=200)
    type_affair = models.CharField(_("Type de dossier"), max_length=30, choices=TYPE_DOSSIER_CHOICES)
    description = models.TextField(_("Description détaillée"), blank=True)
    path_affair = models.CharField(_("Chemin du dossier"), max_length=500, blank=True, editable=False)

    # Relation 
    firm = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='affairs', verbose_name=_("Cabinet"))
    collaborator = models.ForeignKey(Collaborator, on_delete=models.PROTECT, related_name='affairs', verbose_name=_("Collaborateur"), null=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='affairs', verbose_name=_("Client"))

    # Gestion du dossier
    statut = models.CharField(_("Statut"), max_length=15, choices=STATUT_CHOICES, default='NOUVEAU')
    priority = models.CharField(_("Priorité"), max_length=10, choices=PRIORITE_CHOICES, default='NORMALE')

    # Observations et notes
    observations = models.TextField(_("Observations"), blank=True)

    #Archivage et suppression
    is_archived = models.BooleanField(_("Archivé"), default=False)

    # Dates importantes

    creation_date = models.DateField(_("Date d'ouverture"), default=timezone.localdate)
    expiration_date = models.DateField(_("Date d'expiration"), blank=True, null=True) # Date à laquelle le dossier expire ou devient obsolète
    termination_date = models.DateField(_("Date de clôture"), blank=True, null=True) # Date à laquelle le dossier est clôturé ou terminé
    last_activiation_date = models.DateTimeField(_("Date dernière activité"), auto_now=True) # Ici on prend la date de la dernière activité sur le dossier

    class Meta:
        ordering = ['-creation_date']
        verbose_name = _("Affaire")
        verbose_name_plural = _("Affaires")
        indexes = [
            models.Index(fields=['reference_affair']),
            models.Index(fields=['client', 'statut']),
            models.Index(fields=['type_affair', 'statut']),
            models.Index(fields=['termination_date']),
            models.Index(fields=['-last_activiation_date']),
        ]
        unique_together = ('reference_affair', 'firm')  # Assurez-vous que la référence du dossier est unique par cabinet

    def __str__(self):
        return f"{self.reference_affair} - {self.title}"

    def save(self, *args, **kwargs):
        # ===================================================================
        # 1. Génération de la référence dossier (uniquement à la création)
        # ===================================================================
        if not self.reference_affair:
            year = timezone.now().year
            type_prefixes = {
                'CONSTITUTION': 'CONST',
                'MODIFICATION': 'MODIF',
                'DISSOLUTION': 'DISS',
                'CONTENTIEUX': 'CONT',
                'CONSEIL': 'CONS',
                'CONTRAT': 'CNTR',
                'AUDIT': 'AUD',
                'PROPRIETE_INTELLECTUELLE': 'PI',
                'FUSION_ACQUISITION': 'MA',
                'RECOUVREMENT': 'REC',
                'AUTRE': 'AUT',
            }
            prefix = type_prefixes.get(self.type_affair, 'DOS')

            last_dossier = Affair.objects.filter(
                reference_affair__startswith=f"{prefix}-{year}"
            ).order_by('-reference_affair').first()

            new_num = 1
            if last_dossier:
                try:
                    last_num = int(last_dossier.reference_affair.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    pass

            self.reference_affair = f"{prefix}-{year}-{new_num:05d}"

        # ==================================================================
        # 2. Valeurs par défaut importantes                                 
        # ==================================================================
        if not self.creation_date:
            self.creation_date = timezone.now().date()

        if self.statut in ['CLOTURE', 'ANNULE'] and not self.termination_date:
            self.termination_date = timezone.now().date()

        # ===================================================================
        # 3. Chemin physique du dossier client (création unique)
        # ===================================================================
        if not self.path_affair and self.client:
            base_path = os.path.join(settings.MEDIA_ROOT, 'dossiers_clients')
            nom_dossier_client = self.client.creer_nom_dossier_securise()
            self.path_affair = os.path.join(base_path, nom_dossier_client)

        # ===================================================================
        # 4. Sauvegarde principale (une seule fois !)
        # ===================================================================
        super().save(*args, **kwargs)

        # ===================================================================
        # 5. Création physique du dossier sur disque (après sauvegarde)
        # ===================================================================
        if self.path_affair and not os.path.exists(self.path_affair):
            self.creer_dossier_client()

    def creer_dossier_client(self):
        """Crée le dossier physique unique pour le client"""
        try:
            os.makedirs(self.path_affair, exist_ok=True)
        except Exception as e:
            print(f"❌ Erreur création dossier client: {e}")

class Document(models.Model):
    """
        Modèle pour gérer les documents liés à une affaire
    """
    class Relation(models.TextChoices):
        INITIAL = 'INITIAL', _("Document initial")
        ADDED = 'ADDED', _("Ajout")
        UPDATED = 'UPDATED', _("Mise à jour")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affair = models.ForeignKey(Affair, on_delete=models.CASCADE, related_name='documents', verbose_name=_("Affaire"))
    title = models.CharField(_("Titre du document"), max_length=200)
    file = models.FileField(_("Fichier"), upload_to='documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(_("Date de téléchargement"), auto_now_add=True)

    # Évolution du dossier : liaison avec le document dont celui-ci découle
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='children', verbose_name=_("Document précédent"),
    )
    relation = models.CharField(_("Type de liaison"), max_length=10, choices=Relation.choices, default=Relation.INITIAL)
    version = models.PositiveIntegerField(_("Version"), default=1)

    # Position sur l'espace de travail (null = disposition automatique)
    pos_x = models.FloatField(_("Position X"), null=True, blank=True)
    pos_y = models.FloatField(_("Position Y"), null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    def __str__(self):
        return f"{self.title} ({self.affair.reference_affair})"