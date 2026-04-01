from rest_framework import serializers
from apps.core.models import BenchT

class BenchTSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchT
        fields = '__all__'
