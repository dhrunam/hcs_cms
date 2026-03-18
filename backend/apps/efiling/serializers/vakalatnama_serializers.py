from rest_framework import serializers
from apps.core.models import Vakalatnama

class VakalatnamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vakalatnama
        fields = '__all__'
