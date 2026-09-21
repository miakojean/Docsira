from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    ProfileView, 
    ChangePasswordView,
    CollaborateurView,
    CollaboratorCodeView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    # Manage Collaborators endpoints
    path('collaborators/', CollaborateurView.as_view(), name='collaborators'),
    path('collaboratos/code/', CollaboratorCodeView.as_view(), name="Collaborator_code"),
    # JWT token refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
