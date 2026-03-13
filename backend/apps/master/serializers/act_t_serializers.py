from rest_framework import serializers

from apps.core.models import ActT


class ActTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActT
        fields = "__all__"
