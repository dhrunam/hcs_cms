from rest_framework import serializers

from apps.core.models import PurposeT


class PurposeTSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurposeT
        fields = "__all__"