from rest_framework import serializers

from apps.core.models import CaseTypeT


class CaseTypeTSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseTypeT
        fields = "__all__"
