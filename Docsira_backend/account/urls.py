from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    ProfileView, 
    ChangePasswordView,
    CollaborateurView,
    CollaboratorRoleView,
    CollaboratorCodeView,
    OnboardingTourView,
    OnboardingStatusView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('onboarding/', OnboardingStatusView.as_view(), name='onboarding_status'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    # Manage Collaborators endpoints
    path('collaborators/', CollaborateurView.as_view(), name='collaborators'),
    path('collaborators/<uuid:member_id>/role/', CollaboratorRoleView.as_view(), name='collaborator-role'),
    path('collaboratos/code/', CollaboratorCodeView.as_view(), name="Collaborator_code"),
    # JWT token refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('visit-done/', OnboardingTourView.as_view(), name="visite-done")
]
