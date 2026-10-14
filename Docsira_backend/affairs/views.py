from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import AffairSerializer, DocumentSerializer
from .models import Affair, Document
# Create your views here.

class AffairView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AffairSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(firm=request.user)  # Assuming the firm is the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, affair_id=None):
        if affair_id:
            try:
                affair = Affair.objects.get(id=affair_id, firm=request.user)
                serializer = AffairSerializer(affair)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Affair.DoesNotExist:
                return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            affairs = Affair.objects.filter(firm=request.user)
            client_id = request.query_params.get('client')
            if client_id:
                affairs = affairs.filter(client_id=client_id)
            
            # 2. Configuration et application de la pagination
            paginator = PageNumberPagination()
            paginator.page_size = 10 # Définit le nombre de dossiers par page
            
            # 3. Découpage du QuerySet
            paginated_affairs = paginator.paginate_queryset(affairs, request)
            
            # 4. Sérialisation des données paginées uniquement
            serializer = AffairSerializer(paginated_affairs, many=True)
            
            # 5. Renvoi d'une réponse structurée avec les métadonnées de pagination
            return paginator.get_paginated_response(serializer.data)

    def patch(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id, firm=request.user)
            serializer = AffairSerializer(affair, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id, firm=request.user)
            affair.delete()
            return Response({"message": "Affair deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

# N'oubliez pas l'import si ce n'est pas déjà fait en haut de votre fichier :
# from rest_framework.pagination import PageNumberPagination

class DocumentView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, affair_id):
        try:
            # 1. On récupère l'affaire liée pour s'assurer des permissions
            affair = Affair.objects.get(id=affair_id, firm=request.user)
            
            # 2. On récupère tous les documents liés à cette affaire
            documents = affair.documents.all()
            
            # 3. Configuration de la pagination
            paginator = PageNumberPagination()
            paginator.page_size = 10 # Vous pouvez ajuster le nombre de documents par page
            
            # 4. Application de la pagination sur la liste des documents
            paginated_documents = paginator.paginate_queryset(documents, request)
            
            # 5. Sérialisation de la page actuelle uniquement
            serializer = DocumentSerializer(paginated_documents, many=True)
            
            # 6. Renvoi de la réponse formatée avec les métadonnées (count, next, previous)
            return paginator.get_paginated_response(serializer.data)
            
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, affair_id):
            try:
                document = Document.objects.get(id=affair_id, firm=request.user)
                serializer = DocumentSerializer(document, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Document.DoesNotExist:
                return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id, firm=request.user)
            document.delete()
            return Response({"message": "Affair deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Document.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

    