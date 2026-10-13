from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import AffairSerializer
from .models import Affair
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
                affair = Affair.objects.get(id=affair_id)
                serializer = AffairSerializer(affair)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Affair.DoesNotExist:
                return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            affairs = Affair.objects.filter(firm=request.user)
            serializer = AffairSerializer(affairs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id)
            serializer = AffairSerializer(affair, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, affair_id):
        try:
            affair = Affair.objects.get(id=affair_id)
            affair.delete()
            return Response({"message": "Affair deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Affair.DoesNotExist:
            return Response({"error": "Affair not found."}, status=status.HTTP_404_NOT_FOUND)