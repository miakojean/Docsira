from .views import (AffairView, DocumentView, DocumentDownloadView)
from django.urls import path

urlpatterns = [
    path('', AffairView.as_view(), name='affair-list'),
    path('<uuid:affair_id>/', AffairView.as_view(), name='affair-detail'),
    # Documents d'un dossier
    path('<uuid:affair_id>/documents/', DocumentView.as_view(), name='affair-documents'),
    path('document/', DocumentView.as_view(), name='document'),  # ancienne route d'upload (affair dans le corps)
    path('documents/<uuid:document_id>/download/', DocumentDownloadView.as_view(), name='document-download'),
]