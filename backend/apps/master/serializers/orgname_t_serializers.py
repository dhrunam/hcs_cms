from rest_framework import serializers

from apps.core.models import OrgnameT


class OrgnameTSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgnameT
        fields = "__all__"
