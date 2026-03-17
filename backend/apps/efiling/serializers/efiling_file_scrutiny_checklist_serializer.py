from rest_framework import serializers
from apps.core.models import FileScrutinyCheckList

class FileScrutinyCheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileScrutinyCheckList
        fields = '__all__'
