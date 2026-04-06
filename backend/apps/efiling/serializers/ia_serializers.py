from rest_framework import serializers

from apps.core.models import IA
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.efiling.ia_court_fee import ia_court_fee_payment_satisfied, normalize_ia_status


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
            return normalize_ia_status(value)
        return value

    def validate(self, attrs):
        if self.instance is None:
            st = normalize_ia_status(attrs.get("status") or "DRAFT")
            if st == "UNDER_SCRUTINY":
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Create the IA as draft first; after court fee payment, "
                            "update status to submit for scrutiny."
                        )
                    }
                )
            attrs["status"] = st or "DRAFT"
        elif "status" in attrs:
            new_st = normalize_ia_status(attrs["status"])
            old = normalize_ia_status(self.instance.status)
            if new_st == "UNDER_SCRUTINY" and old != "UNDER_SCRUTINY":
                if not ia_court_fee_payment_satisfied(self.instance.pk):
                    raise serializers.ValidationError(
                        {
                            "status": (
                                "Court fee of Rs. 10 must be paid successfully before "
                                "submitting this IA for scrutiny."
                            )
                        }
                    )
            attrs["status"] = new_st
        return attrs

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
