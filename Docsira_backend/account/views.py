from .models import CustomUser
from .serializers import CustomUserSerializer
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
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

        if email:
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response(
                    {'error': 'Email ou mot de passe incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            username = user.username

        user = authenticate(request, username=username, password=password)

        if user is not None:
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
