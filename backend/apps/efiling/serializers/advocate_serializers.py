from rest_framework import serializers

from apps.core.models import AdvocateT


class AdvocateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocateT
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
