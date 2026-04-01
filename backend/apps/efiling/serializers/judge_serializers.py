from rest_framework import serializers
from apps.core.models import JudgeT

class JudgeTSerializer(serializers.ModelSerializer):
    class Meta:
        model = JudgeT
        fields = '__all__'
