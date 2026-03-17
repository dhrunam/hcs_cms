from rest_framework import serializers

from apps.core.models import IA


class IASerializer(serializers.ModelSerializer):
    class Meta:
        model = IA
        fields = [
            "id",
            "e_filing",
            "e_filing_number",
            "ia_number",
            "ia_text",
            "status",
            "disposal_date",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
