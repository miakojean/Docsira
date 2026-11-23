from .views import (
    AffairArchiveView,
    AffairDocumentsView,
    AffairShareLinkView,
    AffairView,
    ArchivedAffairsView,
    DocumentDownloadView,
    DocumentShareLinkView,
    DocumentVersionView,
    DocumentView,
    PublicAffairShareView,
    PublicDocumentShareView,
)
from django.urls import path

urlpatterns = [
    path('archives/', ArchivedAffairsView.as_view(), name='affair-archives'),
    path('', AffairView.as_view(), name='affair-list'),
    path('<uuid:affair_id>/archive/', AffairArchiveView.as_view(), name='affair-archive'),
    path('<uuid:affair_id>/share-links/', AffairShareLinkView.as_view(), name='affair-share-links'),
    path('<uuid:affair_id>/share-links/<uuid:link_id>/', AffairShareLinkView.as_view(), name='affair-share-link-detail'),
    path('<uuid:affair_id>/', AffairView.as_view(), name='affair-detail'),
    path('<uuid:affair_id>/documents/', AffairDocumentsView.as_view(), name='affair-documents'),
    # Documents d'un dossier
    path('documents/', DocumentView.as_view(), name="document-list"),
    path('documents/<uuid:document_id>/download/', DocumentDownloadView.as_view(), name='document-download'),
    path('documents/<uuid:document_id>/versions/', DocumentVersionView.as_view(), name='document-versions'),
    path('documents/<uuid:document_id>/share-links/', DocumentShareLinkView.as_view(), name='document-share-links'),
    path('documents/<uuid:document_id>/share-links/<uuid:link_id>/', DocumentShareLinkView.as_view(), name='document-share-link-detail'),
    path('documents/<uuid:document_id>/', DocumentView.as_view(), name="document-id"),
    # Accès public par lien de partage
    path('share/dossier/<str:token>/', PublicAffairShareView.as_view(), name='public-affair-share'),
    path('share/<str:token>/', PublicDocumentShareView.as_view(), name='public-document-share'),
]