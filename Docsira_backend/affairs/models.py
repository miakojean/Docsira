import os
import uuid
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Relation 
from account.models import CustomUser, Collaborator
from Client.models import Client
from sira.models import SiraCategory, SiraFolderHistory
# Create your models here.

class Affair(models.Model):

    TYPE_DOSSIER_CHOICES = [
        # 1. Constitution, Vie Sociale & Restructuration
        ('CONSTITUTION', 'Constitution de société'),
        ('MODIFICATION', 'Modification statutaire'),
        ('DISSOLUTION', 'Dissolution / Liquidation'),
        ('TRANSFORMATION', 'Transformation de société'),
        ('FUSION_ACQUISITION', 'Fusion / Acquisition (M&A)'),
        ('SECRETARIAT_JURIDIQUE', 'Secrétariat juridique annuel (AGO/AGE)'),
        
        # 2. Comptabilité, Tenue & Révision (Spécial Comptabilité)
        ('COMPTABILITE_TENUE', 'Tenue comptable mensuelle / périodique'),
        ('REVISION_COMPTABLE', 'Révision et arrêté des comptes annuels'),
        ('ETABLISSEMENT_ETATS_FINANCIERS', 'Établissement des états financiers (Bilan, Compte de résultat)'),
        ('CONSOLIDATION_COMPTABLE', 'Consolidation des comptes'),
        ('GESTION_PAIE', 'Gestion de la paie et déclarations sociales'),

        # 3. Fiscalité & Déclarations (Compta & Droit)
        ('FISCALITE_ENTREPRISE', 'Fiscalité des entreprises (Déclarations fiscales)'),
        ('AUDIT_FISCAL', 'Audit et optimisation fiscale'),
        ('ASSISTANCE_CONTROLE_FISCAL', 'Assistance lors d\'un contrôle fiscal ou social'),

        # 4. Contrats, Partenariats & Immobilier
        ('CONTRAT', 'Rédaction et négociation de contrats'),
        ('PARTENARIAT', 'Protocole d\'accord / Partenariat stratégique'),
        ('BAIL_COMMERCIAL', 'Bail commercial / Professionnel'),

        # 5. Contentieux, Recouvrement & Procédures
        ('CONTENTIEUX', 'Contentieux judiciaire (Affaires & Financier)'),
        ('ARBITRAGE_MEDIATION', 'Arbitrage et Médiation'),
        ('RECOUVREMENT', 'Recouvrement de créances et voies d\'exécution'),
        ('PROCEDURE_COLLECTIVE', 'Procédures collectives (Redressement / Liquidation judiciaire)'),

        # 6. Conseil & Audit Global
        ('CONSEIL', 'Conseil juridique et stratégique'),
        ('AUDIT_JURIDIQUE', 'Audit juridique et d\'acquisition (Due Diligence)'),
        ('DROIT_SOCIAL', 'Droit social et relations de travail'),

        # 7. Propriété Intellectuelle & Numérique
        ('PROPRIETE_INTELLECTUELLE', 'Propriété intellectuelle (Marques, Brevets)'),
        ('CONFORMITE_RGPD', 'Conformité réglementaire (RGPD / Protection des données)'),

        # 8. Divers
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
    progression = models.PositiveSmallIntegerField(
        _("Progression (%)"),
        default=10,  # 10 % dès la création du dossier
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        editable=False,
    )

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
                # Constitution, Vie Sociale & Restructuration
                'CONSTITUTION': 'CONST',
                'MODIFICATION': 'MODIF',
                'DISSOLUTION': 'DISS',
                'TRANSFORMATION': 'TRANS',
                'FUSION_ACQUISITION': 'MA',
                'SECRETARIAT_JURIDIQUE': 'SEC',
                
                # Comptabilité, Tenue & Révision
                'COMPTABILITE_TENUE': 'COMP',
                'REVISION_COMPTABLE': 'REV',
                'ETABLISSEMENT_ETATS_FINANCIERS': 'EF',
                'CONSOLIDATION_COMPTABLE': 'CC',
                'GESTION_PAIE': 'PAIE',

                # Fiscalité & Déclarations
                'FISCALITE_ENTREPRISE': 'FISC',
                'AUDIT_FISCAL': 'AUDF',
                'ASSISTANCE_CONTROLE_FISCAL': 'CTRL',

                # Contrats, Partenariats & Immobilier
                'CONTRAT': 'CNTR',
                'PARTENARIAT': 'PART',
                'BAIL_COMMERCIAL': 'BAIL',

                # Contentieux, Recouvrement & Procédures
                'CONTENTIEUX': 'CONT',
                'ARBITRAGE_MEDIATION': 'ARBIT',
                'RECOUVREMENT': 'REC',
                'PROCEDURE_COLLECTIVE': 'PROC',

                # Conseil & Audit Global
                'CONSEIL': 'CONS',
                'AUDIT_JURIDIQUE': 'AUD',
                'DROIT_SOCIAL': 'SOC',

                # Propriété Intellectuelle & Numérique
                'PROPRIETE_INTELLECTUELLE': 'PI',
                'CONFORMITE_RGPD': 'RGPD',

                # Divers
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

    def calculer_progression_sira(self):
        """
        Calcule la progression selon les 5 catégories SIRA :
        - Identification : 45%
        - Constitution : 60%
        - Procédures : 75%
        - Livrables : 90%
        - Clôture : 100%
        """
        if self.statut in ['CLOTURE', 'TERMINE']:
            return 100

        docs = self.documents.all()
        categories = set(docs.values_list('category', flat=True))

        if 'CLOTURE' in categories or self.statut == 'CLOTURE':
            return 100
        if 'LIVRABLES' in categories:
            return 90
        if 'PROCEDURES' in categories:
            return 75
        if 'CONSTITUTION' in categories:
            return 60
        if 'IDENTIFICATION' in categories:
            return 45
        
        return 10 # Valeur par défaut à la création

    def recalculer_progression(self):
        """Met à jour la progression sans repasser par save() (évite la logique de référence/dossier physique)."""
        new_prog = self.calculer_progression_sira()
        Affair.objects.filter(pk=self.pk).update(
            progression=new_prog,
            last_activiation_date=timezone.now(),  # update() ne déclenche pas auto_now
        )
        self.progression = new_prog
        return new_prog

class DocumentQuerySet(models.QuerySet):
    def delete(self):
        # Couvre queryset.delete() et l'action « supprimer la sélection » de l'admin
        affair_ids = set(self.values_list('affair_id', flat=True))
        with transaction.atomic():
            result = super().delete()
            for affair in Affair.objects.filter(pk__in=affair_ids):
                affair.recalculer_progression()
        return result


def document_upload_path(instance, filename):
    """Place new documents in the client directory associated with the affair."""
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    client_directory = os.path.abspath(instance.affair.path_affair) if instance.affair.path_affair else ""

    try:
        is_inside_media_root = (
            client_directory
            and os.path.normcase(os.path.commonpath([media_root, client_directory]))
            == os.path.normcase(media_root)
        )
    except ValueError:
        is_inside_media_root = False

    if is_inside_media_root:
        relative_directory = os.path.relpath(client_directory, media_root)
    else:
        # Fallback for legacy affairs without a valid stored path.
        client_folder = instance.affair.client.creer_nom_dossier_securise()
        relative_directory = os.path.join("dossiers_clients", client_folder)

    safe_filename = os.path.basename(filename.replace("\\", "/"))
    return os.path.join(relative_directory, safe_filename).replace("\\", "/")

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
    file = models.FileField(_("Fichier"), upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(_("Date de téléchargement"), auto_now_add=True)

    # Évolution du dossier : liaison avec le document dont celui-ci découle
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='children', verbose_name=_("Document précédent"),
    )
    relation = models.CharField(_("Type de liaison"), max_length=10, choices=Relation.choices, default=Relation.INITIAL)
    version = models.PositiveIntegerField(_("Version"), default=1)

    category = models.CharField(
        _("Catégorie SIRA"), 
        max_length=30, 
        choices=SiraCategory.choices, 
        default=SiraCategory.IDENTIFICATION
    )
    valide = models.BooleanField(_("Document validé"), default=False)

    # Position sur l'espace de travail (null = disposition automatique)
    pos_x = models.FloatField(_("Position X"), null=True, blank=True)
    pos_y = models.FloatField(_("Position Y"), null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    objects = DocumentQuerySet.as_manager()

    def __str__(self):
        return f"{self.title} ({self.affair.reference_affair})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_progression = self.affair.progression
        
        super().save(*args, **kwargs)
        
        # Recalcul de la progression via SIRA
        new_progression = self.affair.calculer_progression_sira()
        
        if old_progression != new_progression or is_new:
            self.affair.progression = new_progression
            self.affair.save(update_fields=['progression'])
            
            # Enregistrement automatique dans le module d'historique SIRA
            SiraFolderHistory.objects.create(
                affair_id=self.affair.id,
                previous_progression=old_progression,
                new_progression=new_progression,
                action_type="AJOUT_DOCUMENT" if is_new else "MAJ_DOCUMENT",
                document_title=self.title,
                category=self.category,
                author=str(self.affair.collaborator) if self.affair.collaborator else "Système",
                details=f"Ajout/Mise à jour du document '{self.title}' dans la catégorie {self.category}."
            )

    def delete(self, *args, **kwargs):
        affair = self.affair
        old_progression = affair.progression
        doc_title = self.title
        doc_category = self.category
        author_name = str(affair.collaborator) if affair.collaborator else "Système"

        with transaction.atomic():
            result = super().delete(*args, **kwargs)
            new_progression = affair.recalculer_progression()

            SiraFolderHistory.objects.create(
                affair_id=affair.id,
                previous_progression=old_progression,
                new_progression=new_progression,
                action_type="SUPPRESSION_DOCUMENT",
                document_title=doc_title,
                category=doc_category,
                author=author_name,
                details=f"Suppression du document '{doc_title}' ({doc_category})."
            )
        return result