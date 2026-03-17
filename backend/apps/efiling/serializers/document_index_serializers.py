from rest_framework import serializers
from apps.core.models import DocumentIndex

class DocumentIndexSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentIndex
        fields = ['name', 
        
       
        read_only_fields = ['id']
