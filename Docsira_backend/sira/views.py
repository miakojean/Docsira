from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from affairs.models import Affair
from .models import SiraFolderHistory
from .serializers import SiraFolderHistorySerializer

class SiraHistoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class SiraHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_firm(self, user):
        if hasattr(user, 'collaborator_profile'):
            return user.collaborator_profile.main_account
        return user

    def get(self, request, affair_id):
        """Récupère l'historique complet de versionnage d'un dossier donné du cabinet."""
        firm = self._get_firm(request.user)
        if not Affair.objects.filter(pk=affair_id, firm=firm).exists():
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        histories = SiraFolderHistory.objects.filter(affair_id=affair_id)
        action_type = (request.query_params.get('action_type') or '').strip()
        if action_type:
            histories = histories.filter(action_type=action_type)
        
        paginator = SiraHistoryPagination()
        paginated_histories = paginator.paginate_queryset(histories, request)
        
        serializer = SiraFolderHistorySerializer(paginated_histories, many=True)
        return paginator.get_paginated_response(serializer.data)