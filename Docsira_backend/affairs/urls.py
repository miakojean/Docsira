from .views import (
    AffairArchiveView,
    AffairDocumentsView,
    AffairView,
    ArchivedAffairsView,
    DocumentView,
)
from django.urls import path

urlpatterns = [
    path('archives/', ArchivedAffairsView.as_view(), name='affair-archives'),
    path('', AffairView.as_view(), name='affair-list'),
    path('<uuid:affair_id>/archive/', AffairArchiveView.as_view(), name='affair-archive'),
    path('<uuid:affair_id>/', AffairView.as_view(), name='affair-detail'),
    path('<uuid:affair_id>/documents/', AffairDocumentsView.as_view(), name='affair-documents'),
    # Documents d'un dossier
    path('documents/',DocumentView.as_view(), name="document-list"),
    path('documents/<uuid:document_id>/', DocumentView.as_view(), name="document-id")
]