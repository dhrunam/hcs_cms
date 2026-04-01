from rest_framework import serializers

from apps.core.models import IA
from apps.efiling.party_display import build_petitioner_vs_respondent


class IASerializer(serializers.ModelSerializer):
    petitioner_vs_respondent = serializers.SerializerMethodField(read_only=True)

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
            "petitioner_vs_respondent",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "petitioner_vs_respondent"]

    def validate_status(self, value):
        if value:
            normalized = str(value).strip().upper().replace(" ", "_")
            return normalized
        return value

    def get_petitioner_vs_respondent(self, obj):
        ef = getattr(obj, "e_filing", None)
        if ef is None:
            return ""
        preferred = str(getattr(ef, "petitioner_name", None) or "").strip()
        if preferred:
            return preferred
        return build_petitioner_vs_respondent(
            ef,
            fallback_petitioner_name=getattr(ef, "petitioner_name", None) or "",
        )
