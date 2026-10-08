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