from rest_framework import serializers

from apps.core.models import OrgtypeT


class OrgtypeTSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgtypeT
        fields = "__all__"
