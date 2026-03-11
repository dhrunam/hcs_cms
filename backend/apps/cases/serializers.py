from rest_framework import serializers

from .models import Case


class CaseSerializer(serializers.ModelSerializer):
    """Serializer for the Case model."""

    created_by_email = serializers.EmailField(
        source="created_by.email",
        read_only=True,
    )
    case_type_display = serializers.CharField(
        source="get_case_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Case
        fields = [
            "id",
            "case_number",
            "case_type",
            "case_type_display",
            "case_title",
            "petitioner_name",
            "respondent_name",
            "filed_date",
            "status",
            "status_display",
            "bench",
            "judge_name",
            "description",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_email",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]
