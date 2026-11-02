from django.urls import path
from .views import SiraHistoryView

urlpatterns = [
    path('affairs/<uuid:affair_id>/history/', SiraHistoryView.as_view(), name='sira-affair-history'),
]