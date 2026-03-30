from rest_framework import serializers

from apps.efiling.models import EfilingNotification


class EfilingNotificationSerializer(serializers.ModelSerializer):
    e_filing_number = serializers.SerializerMethodField()

    class Meta:
        model = EfilingNotification
        fields = ["id", "role", "notification_type", "message", "e_filing", "ia", "link_url", "created_at", "e_filing_number"]

    def get_e_filing_number(self, obj):
        return obj.e_filing.e_filing_number if obj.e_filing else None
