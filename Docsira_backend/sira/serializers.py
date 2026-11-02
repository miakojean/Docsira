from rest_framework import serializers
from .models import SiraFolderHistory

class SiraFolderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SiraFolderHistory
        fields = '__all__'