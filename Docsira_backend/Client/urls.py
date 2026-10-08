from django.urls import path
from .views import ManageClient, RestoreClient

urlpatterns = [
    path('', ManageClient.as_view(), name='client'),
    path('<uuid:client_id>/', ManageClient.as_view(), name='client_detail'),
    path('<uuid:client_id>/restore/', RestoreClient.as_view(), name='client_restore'),
]
