from rest_framework import serializers
from django.utils import timezone
from django.db import models
from account.models import CustomUser
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    # Champs calculés en lecture seule
    nom_complet = serializers.ReadOnlyField()
    
    # Relations
    charge_de_clientele = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True
    )
    
    # CORRECTION: Gérer date_premier_contact correctement
    date_creation = serializers.DateTimeField(read_only=True)
    date_modification = serializers.DateTimeField(read_only=True)
    date_premier_contact = serializers.DateField(
        required=False,
        allow_null=True,
        default=timezone.now().date()  # Date par défaut (pas datetime)
    )
    
    class Meta:
        model = Client
        fields = [
            'id',
            # Informations générales
            'type_client', 'statut', 'reference_client',
            
            # Personne Physique
            'nom', 'prenoms', 'date_naissance', 'lieu_naissance',
            
            # Personne Morale
            'raison_sociale', 'forme_juridique', 'numero_rccm',
            'numero_cc', 'capital_social',
            
            # Coordonnées
            'adresse', 'ville', 'commune', 'pays', 'telephone_1',
            'telephone_2', 'email',
            
            # Informations juridiques complémentaires 
            'representant_legal_nom', 'representant_legal_fonction',
            
            # Gestion administrative
            'date_creation', 'date_modification', 'date_premier_contact',
            'notes',
            
            # Relations
            'charge_de_clientele',
            
            # Champs calculés
            'nom_complet'
        ]
        read_only_fields = ['reference_client', 'date_creation', 'date_modification']

    def to_internal_value(self, data):
        """
        CORRECTION: Convertir les datetime en date avant validation
        """
        # Copier les données pour ne pas modifier l'original
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Gérer date_premier_contact
        if 'date_premier_contact' in data and data['date_premier_contact']:
            date_str = str(data['date_premier_contact'])
            # Si c'est un datetime (contient 'T'), extraire seulement la date
            if 'T' in date_str:
                data['date_premier_contact'] = date_str.split('T')[0]
        
        # Gérer date_naissance
        if 'date_naissance' in data and data['date_naissance']:
            date_str = str(data['date_naissance'])
            if 'T' in date_str:
                data['date_naissance'] = date_str.split('T')[0]
        
        return super().to_internal_value(data)
    
    def validate(self, data):
        type_client = data.get('type_client', self.instance.type_client if self.instance else None)
        instance_pk = self.instance.pk if self.instance else None

        # 1. Champs obligatoires selon le type (inchangé)
        if type_client == 'PERSONNE_PHYSIQUE':
            if not data.get('nom'):
                raise serializers.ValidationError({'nom': 'Le nom est obligatoire pour une personne physique.'})
            if not data.get('prenoms'):
                raise serializers.ValidationError({'prenoms': 'Le ou les prénoms sont obligatoires pour une personne physique.'})
        elif type_client == 'PERSONNE_MORALE':
            if not data.get('raison_sociale'):
                raise serializers.ValidationError({'raison_sociale': 'La raison sociale est obligatoire pour une personne morale.'})

        # Propriétaire du client : celui du payload, sinon celui de l'instance, sinon l'utilisateur connecté
        request = self.context.get('request')
        owner = data.get(
            'charge_de_clientele',
            self.instance.charge_de_clientele if self.instance else (request.user if request else None)
        )

        # Base de comparaison : uniquement les clients de CET utilisateur, hors corbeille
        base_qs = Client.objects.filter(charge_de_clientele=owner, is_deleted=False)
        if instance_pk:
            base_qs = base_qs.exclude(pk=instance_pk)

        # 2. Unicité email / téléphone (par utilisateur)
        q_filters = models.Q()
        if data.get('email'):
            q_filters |= models.Q(email=data['email'])
        if data.get('telephone_1'):
            q_filters |= models.Q(telephone_1=data['telephone_1'])

        if q_filters and base_qs.filter(q_filters).exists():
            raise serializers.ValidationError("Vous avez déjà un client avec cet email ou ce téléphone 1.")

        # 3. Anti-duplication par type (par utilisateur)
        if type_client == 'PERSONNE_PHYSIQUE':
            nom = data.get('nom', self.instance.nom if self.instance else None)
            prenoms = data.get('prenoms', self.instance.prenoms if self.instance else None)
            date_naissance = data.get('date_naissance', self.instance.date_naissance if self.instance else None)

            if nom and prenoms and date_naissance:
                if base_qs.filter(
                    type_client='PERSONNE_PHYSIQUE',
                    nom=nom, prenoms=prenoms, date_naissance=date_naissance
                ).exists():
                    raise serializers.ValidationError({
                        'non_field_errors': "Vous avez déjà un client Personne Physique avec ces Nom, Prénom(s) et Date de naissance."
                    })

        elif type_client == 'PERSONNE_MORALE':
            raison_sociale = data.get('raison_sociale', self.instance.raison_sociale if self.instance else None)
            numero_rccm = data.get('numero_rccm', self.instance.numero_rccm if self.instance else None)
            numero_cc = data.get('numero_cc', self.instance.numero_cc if self.instance else None)

            pm_q = models.Q()
            if raison_sociale:
                pm_q |= models.Q(raison_sociale__iexact=raison_sociale)
            if numero_rccm:
                pm_q |= models.Q(numero_rccm__iexact=numero_rccm)
            if numero_cc:
                pm_q |= models.Q(numero_cc__iexact=numero_cc)

            if pm_q and base_qs.filter(type_client='PERSONNE_MORALE').filter(pm_q).exists():
                raise serializers.ValidationError({
                    'non_field_errors': "Vous avez déjà un client Personne Morale avec cette Raison Sociale, ce Numéro RCCM ou ce Numéro CC."
                })

        return super().validate(data)


# Serializer léger pour les listes
class ClientListSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()
    charge_de_clientele_nom = serializers.CharField(
        source='charge_de_clientele.get_full_name', 
        read_only=True
    )
    nombre_dossiers = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'reference_client', 'type_client', 'statut',
            'nom_complet', 'telephone_1', 'email', 'ville',
            'charge_de_clientele_nom', 'date_creation', 'nombre_dossiers'
        ]
    
    def get_nombre_dossiers(self, obj):
        return obj.dossiers.count()
