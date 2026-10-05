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
        """
        Renforce la validation :
        1. Champs obligatoires selon le type_client.
        2. Unicité des identifiants (Email, Téléphone 1).
        3. Unicité du client (combinaison PP ou Raison Sociale/RCCM PM).
        """
        # 1. Validation conditionnelle des champs obligatoires (cohérence)
        type_client = data.get('type_client', self.instance.type_client if self.instance else None)

        if type_client == 'PERSONNE_PHYSIQUE':
            if not data.get('nom'):
                raise serializers.ValidationError({'nom': 'Le nom est obligatoire pour une personne physique.'})
            if not data.get('prenoms'):
                raise serializers.ValidationError({'prenoms': 'Le ou les prénoms sont obligatoires pour une personne physique.'})
        
        elif type_client == 'PERSONNE_MORALE':
            if not data.get('raison_sociale'):
                raise serializers.ValidationError({'raison_sociale': 'La raison sociale est obligatoire pour une personne morale.'})

        # 2. Vérification d'unicité pour l'email et le téléphone
        q_filters = models.Q()
        instance_pk = self.instance.pk if self.instance else None

        if data.get('email') and data['email']:
            q_filters |= models.Q(email=data['email'])

        if data.get('telephone_1') and data['telephone_1']:
            q_filters |= models.Q(telephone_1=data['telephone_1'])

        if q_filters:
            if instance_pk:
                if Client.objects.filter(q_filters).exclude(pk=instance_pk).exists():
                    raise serializers.ValidationError("Un client avec cet email ou ce téléphone 1 existe déjà.")
            else:
                if Client.objects.filter(q_filters).exists():
                    raise serializers.ValidationError("Un client avec cet email ou ce téléphone 1 existe déjà.")

        # 3. Vérification d'unicité par type de client (Anti-duplication)
        if type_client == 'PERSONNE_PHYSIQUE':
            nom = data.get('nom', self.instance.nom if self.instance else None)
            prenoms = data.get('prenoms', self.instance.prenoms if self.instance else None)
            date_naissance = data.get('date_naissance', self.instance.date_naissance if self.instance else None)
            
            # Vérifie la combinaison nom/prenoms/date_naissance si ces champs sont définis
            if nom and prenoms and date_naissance:
                dupe_check = Client.objects.filter(
                    type_client='PERSONNE_PHYSIQUE',
                    nom=nom,
                    prenoms=prenoms,
                    date_naissance=date_naissance
                )
                if instance_pk:
                    dupe_check = dupe_check.exclude(pk=instance_pk)
                
                if dupe_check.exists():
                    raise serializers.ValidationError({
                        'non_field_errors': "Un client Personne Physique avec ce Nom, Prénom(s) et Date de naissance existe déjà."
                    })
            
        elif type_client == 'PERSONNE_MORALE':
            raison_sociale = data.get('raison_sociale', self.instance.raison_sociale if self.instance else None)
            numero_rccm = data.get('numero_rccm', self.instance.numero_rccm if self.instance else None)
            numero_cc = data.get('numero_cc', self.instance.numero_cc if self.instance else None)
            
            dupe_check = Client.objects.filter(type_client='PERSONNE_MORALE')
            
            # Utilise au moins un identifiant unique PM
            pm_q_filters = models.Q()
            if raison_sociale:
                pm_q_filters |= models.Q(raison_sociale__iexact=raison_sociale) # Case-insensitive
            if numero_rccm:
                pm_q_filters |= models.Q(numero_rccm__iexact=numero_rccm)
            if numero_cc:
                pm_q_filters |= models.Q(numero_cc__iexact=numero_cc)
            
            if pm_q_filters:
                dupe_check = dupe_check.filter(pm_q_filters)
                if instance_pk:
                    dupe_check = dupe_check.exclude(pk=instance_pk)

                if dupe_check.exists():
                    raise serializers.ValidationError({
                        'non_field_errors': "Un client Personne Morale avec cette Raison Sociale, ce Numéro RCCM ou ce Numéro CC existe déjà."
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
