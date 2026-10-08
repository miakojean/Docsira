from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ClientSerializer
from .models import Client
from rest_framework.response import Response
from rest_framework import status
from account.models import CustomUser
from django.db import transaction

def get_firm_users(user):
    if user.account_type == CustomUser.AccountType.COLLABORATOR:
        try:
            main_account = user.collaborator_profile.main_account
        except Exception:
            main_account = user
    else:
        main_account = user
        
    collaborators = CustomUser.objects.filter(collaborator_profile__main_account=main_account)
    return [main_account] + list(collaborators)

class ManageClient(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1- On va serializer la requête (on nomme la variable 'serializer' pour plus de clarté)
        serializer = ClientSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # 2- On sauvegarde l'instance dans la base de données
            # Le créateur devient automatiquement le propriétaire du client.
            serializer.save(charge_de_clientele=request.user)

            # 3- On retourne les données fraîchement créées
            return Response({
                'success': True,
                'message': 'Client créé avec succès',
                'client': serializer.data
            }, status=status.HTTP_201_CREATED)

        else:
            # 4- On retourne les erreurs de validation en utilisant le bon nom de variable
            return Response({
                'success': False,
                'message': 'Erreur de validation',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        is_trash = request.query_params.get('trash', 'false').lower() == 'true'
        
        users_to_include = get_firm_users(request.user)
        clients = Client.objects.filter(charge_de_clientele__in=users_to_include, is_deleted=is_trash)

        serializer = ClientSerializer(clients, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, client_id, *args, **kwargs):
        try:
            users_to_include = get_firm_users(request.user)
            client = Client.objects.get(id=client_id, charge_de_clientele__in=users_to_include)
            serializer = ClientSerializer(client, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                with transaction.atomic():
                    updated_client = serializer.save()
                                     
                    
                client_serializer = ClientSerializer(updated_client)
                return Response({
                    'success': True,
                    'message': 'Client mis à jour avec succès',
                    'client': client_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Erreur de validation',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Client.DoesNotExist:
            return Response({
                'message': 'Client non trouvé',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur interne du serveur',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, client_id, *args, **kwargs):
        try:
            users_to_include = get_firm_users(request.user)
            client = Client.objects.get(id=client_id, charge_de_clientele__in=users_to_include)

            serializer = ClientSerializer(client, data=request.data, partial=True, context={'request': request})

            if serializer.is_valid():
                with transaction.atomic():
                    updated_client = serializer.save()
                                     
                client_serializer = ClientSerializer(updated_client)
                return Response({
                    'success': True,
                    'message': 'Changements mineurs appliqués avec succès',
                    'client': client_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Erreur de validation',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Client.DoesNotExist:
            return Response({
                'message': 'Client non trouvé',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur interne du serveur',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, client_id, *args, **kwargs):
        try:
            users_to_include = get_firm_users(request.user)
            client = Client.objects.get(id=client_id, charge_de_clientele__in=users_to_include)
            
            # Mise à la corbeille (Soft Delete)
            client.is_deleted = True
            client.save(update_fields=['is_deleted'])
            
            return Response({
                'success': True,
                'message': 'Client déplacé vers la corbeille avec succès'
            }, status=status.HTTP_200_OK)

        except Client.DoesNotExist:
            return Response({
                'message': 'Client non trouvé',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur interne du serveur',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RestoreClient(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_id, *args, **kwargs):
        try:
            users_to_include = get_firm_users(request.user)
            client = Client.objects.get(id=client_id, charge_de_clientele__in=users_to_include)
            
            client.is_deleted = False
            client.save(update_fields=['is_deleted'])
            
            return Response({
                'success': True,
                'message': 'Client restauré avec succès'
            }, status=status.HTTP_200_OK)

        except Client.DoesNotExist:
            return Response({
                'message': 'Client non trouvé',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur interne du serveur',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PermanentDeleteClient(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, client_id, *args, **kwargs):
        try:
            user = request.user
            
            # 1. Déterminer le "propriétaire" du cabinet et vérifier les permissions
            if hasattr(user, 'collaborator_profile'):
                collab_profile = user.collaborator_profile
                
                # Si le collaborateur n'est pas un administrateur, on bloque l'action
                if collab_profile.role != 'admin': 
                    return Response({
                        'success': False,
                        'message': 'Action refusée : Seul un administrateur peut supprimer définitivement un client.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Le client appartient au compte principal de ce collaborateur
                owner = collab_profile.main_account
            else:
                # L'utilisateur connecté est le compte principal (Firme/Individu)
                owner = user

            # 2. Récupérer le client en s'assurant qu'il appartient bien au cabinet 
            # (On utilise 'owner' pour sécuriser la vérification)
            client = Client.objects.get(id=client_id, charge_de_clientele=owner)

            # 3. Suppression physique définitive de la base de données
            client.delete()
            
            return Response({
                'success': True,
                'message': 'Le client a été supprimé définitivement du système.'
            }, status=status.HTTP_200_OK)

        except Client.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Client introuvable ou vous n\'avez pas l\'autorisation de le supprimer.'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur interne du serveur',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)