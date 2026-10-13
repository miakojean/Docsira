from .views import AffairView
from django.urls import path

urlpatterns = [
    path('', AffairView.as_view(), name='affair-list'),
]