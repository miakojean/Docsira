from .models import CustomUser, Collaborator, CollaboratorInvitation, ActivationCode
from .serializers import CustomUserSerializer, CollaboratorSerializer, CollaboratorInvitationSerializer, ActivationCodeSerializer
from .utils import generate_temporary_password, send_invitation_email
from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone

# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=200)

    def put(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Le refresh token est requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {'error': 'Refresh token invalide ou déjà révoqué.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        if not password or (not email and not username):

            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        if email or (username and '@' in username):
            email = email or username
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response(
                    {'error': 'Email ou mot de passe incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            username = user.username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            with transaction.atomic():
                invitations = CollaboratorInvitation.objects.select_for_update().filter(
                    user=user,
                    accepted_at__isnull=True,
                )
                for invitation in invitations:
                    Collaborator.objects.get_or_create(
                        main_account=invitation.main_account,
                        user=user,
                        defaults={'role': invitation.role},
                    )
                    invitation.accepted_at = timezone.now()
                    invitation.save(update_fields=['accepted_at'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Identifiants incorrects.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

# ====================== Collaborateurs =================================

class CollaborateurView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CollaboratorSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            role = serializer.validated_data.get('role', Collaborator.Roles.VIEWER)

            try:
                with transaction.atomic():
                    user = CustomUser.objects.filter(email__iexact=email).first()
                    invitation = None
                    if user:
                        invitation = CollaboratorInvitation.objects.filter(
                            main_account=request.user,
                            user=user,
                        ).first()
                    if invitation and invitation.accepted_at is not None:
                        return Response(
                            {'error': 'Ce collaborateur est déjà lié à ce compte.'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if user and not invitation and user.has_usable_password():
                        return Response(
                            {'error': 'Cette adresse possède déjà un compte. Utilisez son mot de passe.'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    if not user:
                        username = email.split('@')[0]
                        suffix = 1
                        base_username = username
                        while CustomUser.objects.filter(username=username).exists():
                            username = f'{base_username}{suffix}'
                            suffix += 1
                        user = CustomUser.objects.create(
                            email=email,
                            username=username,
                            account_type=CustomUser.AccountType.COLLABORATOR,
                        )

                    temporary_password = generate_temporary_password()
                    user.set_password(temporary_password)
                    user.save(update_fields=['password'])
                    invitation, created = CollaboratorInvitation.objects.get_or_create(
                        main_account=request.user,
                        user=user,
                        defaults={'role': role},
                    )
                    if not created:
                        invitation.role = role
                        invitation.save(update_fields=['role'])
                    send_invitation_email(user, temporary_password)

                response_serializer = CollaboratorInvitationSerializer(invitation)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "Ce collaborateur est déjà invité pour ce compte."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Si l'email n'est pas valide ou manquant
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        collab_data = []
        
        # 1. Accepted collaborators
        collaborators = Collaborator.objects.filter(main_account=request.user).select_related('user')
        for c in collaborators:
            collab_data.append({
                'id': f'collab_{c.id}',
                'email': c.user.email,
                'username': c.user.username,
                'role': c.role,
                'status': 'accepted',
                'created_at': c.created_at
            })
            
        # 2. Pending invitations
        invitations = CollaboratorInvitation.objects.filter(
            main_account=request.user, 
            accepted_at__isnull=True
        ).select_related('user')
        for i in invitations:
            collab_data.append({
                'id': f'inv_{i.id}',
                'email': i.user.email,
                'username': i.user.username,
                'role': i.role,
                'status': 'pending',
                'created_at': i.created_at
            })

        # Sort by creation date
        collab_data.sort(key=lambda x: x['created_at'], reverse=True)

        return Response(collab_data, status=status.HTTP_200_OK)

class CollaboratorCodeView(APIView):
    permission_classes = [AllowAny] # Permet à un utilisateur non connecté de valider son code

    def get(self, request):
        activation_codes = ActivationCode.objects.filter(user=request.user)
        serializer = ActivationCodeSerializer(activation_codes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 1. Récupérer le code envoyé par le frontend (ton composant Vue.js)
        code_saisi = request.data.get('code')

        if not code_saisi:
            return Response(
                {"error": "Veuillez fournir un code d'activation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Chercher ce code dans la base de données
        activation = ActivationCode.objects.filter(code=code_saisi).first()

        # 3. Vérifier que le code existe bien
        if not activation:
            return Response(
                {"error": "Code invalide ou inexistant."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Vérifier que le code n'a pas déjà été utilisé
        if activation.is_used:
            return Response(
                {"error": "Ce code a déjà été utilisé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Vérifier que le code n'est pas expiré (en comparant avec expires_at)[cite: 1]
        if timezone.now() > activation.expires_at:
            return Response(
                {"error": "Ce code a expiré. Veuillez demander un nouveau code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6. Le code est valide ! On le marque comme utilisé.
        activation.is_used = True
        activation.save()

        # 7. (Optionnel) Tu peux renvoyer l'ID de l'utilisateur ou un jeton temporaire
        # pour permettre à ton frontend de l'identifier lors de la création de son mot de passe.
        return Response({
            "message": "Code validé avec succès.",
            "user_id": activation.user.id,
            "email": activation.user.email
        }, status=status.HTTP_200_OK)
