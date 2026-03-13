from rest_framework import serializers

from apps.core.models import District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"
