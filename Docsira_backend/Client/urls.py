from django.urls import path
from .views import ManageClient


urlpatterns = [
    path('', ManageClient.as_view(), name='client')
]
