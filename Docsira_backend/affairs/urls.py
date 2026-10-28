from .views import AffairDocumentsView, AffairView, DocumentView
from django.urls import path

urlpatterns = [
    path('', AffairView.as_view(), name='affair-list'),
    path('<uuid:affair_id>/', AffairView.as_view(), name='affair-detail'),
    path('<uuid:affair_id>/documents/', AffairDocumentsView.as_view(), name='affair-documents'),
    # Documents d'un dossier
    path('documents/',DocumentView.as_view(), name="document-list"),
    path('documents/<uuid:document_id>/', DocumentView.as_view(), name="document-id")
]