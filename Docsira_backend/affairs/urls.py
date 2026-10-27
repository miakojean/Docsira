from .views import (AffairView)
from django.urls import path

urlpatterns = [
    path('', AffairView.as_view(), name='affair-list'),
    path('<uuid:affair_id>/', AffairView.as_view(), name='affair-detail'),
    # Documents d'un dossier
]