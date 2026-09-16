from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # Manage Collaborators endpoints
    
    # JWT token refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
