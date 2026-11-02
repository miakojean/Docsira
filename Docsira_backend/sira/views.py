from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import SiraFolderHistory
from .serializers import SiraFolderHistorySerializer

class SiraHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, affair_id):
        """Récupère l'historique complet de versionnage d'un dossier donné"""
        histories = SiraFolderHistory.objects.filter(affair_id=affair_id)
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_histories = paginator.paginate_queryset(histories, request)
        
        serializer = SiraFolderHistorySerializer(paginated_histories, many=True)
        return paginator.get_paginated_response(serializer.data)