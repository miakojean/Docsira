from django.urls import path
from .views import ManageClient, RestoreClient, PermanentDeleteClient

urlpatterns = [
    path('', ManageClient.as_view(), name='client'),
    path('<uuid:client_id>/', ManageClient.as_view(), name='client_detail'),
    path('<uuid:client_id>/restore/', RestoreClient.as_view(), name='client_restore'),
    path('<uuid:client_id>/permanent-delete/', PermanentDeleteClient.as_view())
]
