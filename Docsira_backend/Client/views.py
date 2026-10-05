from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ClientSerializer
from rest_framework.response import Response
from rest_framework import status

class ManageClient(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1- On va serializer la requête (on nomme la variable 'serializer' pour plus de clarté)
        serializer = ClientSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # 2- On sauvegarde l'instance dans la base de données
            serializer.save()

            # 3- On retourne les données fraîchement créées
            return Response({
                'success': True,
                'message': 'Client créé avec succès',
                'client': serializer.data
            }, status=status.HTTP_201_CREATED)

        else:
            # 4- On retourne les erreurs de validation en utilisant le bon nom de variable
            return Response({
                'success': False,
                'message': 'Erreur de validation',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        pass
