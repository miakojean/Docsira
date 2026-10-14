from .views import AffairView, DocumentView
from django.urls import path

urlpatterns = [
    path('', AffairView.as_view(), name='affair-list'),
    path('<uuid:affair_id>/', AffairView.as_view(), name='affair-detail'),
    path('document/', DocumentView.as_view(), name='document'),
    path('<uuid:document_id>', DocumentView.as_view(), name="document-affair")
]