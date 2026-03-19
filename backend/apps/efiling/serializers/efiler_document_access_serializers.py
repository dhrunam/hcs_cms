from rest_framework import serializers
from apps.core.models import EfilerDocumentAccess

class EfilerDocumentAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = EfilerDocumentAccess
        fields = '__all__'
