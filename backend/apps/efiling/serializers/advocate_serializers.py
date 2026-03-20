from rest_framework import serializers

from apps.core.models import AdvocateT


class AdvocateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocateT
        fields = [
            "adv_code",
            "adv_name",
            "ladv_name",
            "adv_reg",
            "email",
            "adv_mobile",
            "adv_phone",
            "adv_full_name",
            "adv_gender",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
