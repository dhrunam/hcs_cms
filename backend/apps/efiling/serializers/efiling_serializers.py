from rest_framework import serializers

from apps.core.models import CaseTypeT, Efiling
from apps.efiling.party_display import build_petitioner_vs_respondent


class EfilingCaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseTypeT
        fields = ['id', 'case_type', 'type_name', 'full_form']


class EfilingSerializer(serializers.ModelSerializer):
    case_type = serializers.PrimaryKeyRelatedField(
        queryset=CaseTypeT.objects.all(),
        required=False,
        allow_null=True,
    )
    petitioner_vs_respondent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Efiling
        fields = [
            'id',
            'case_type',
            'bench',
            'petitioner_name',
            'petitioner_contact',
            'e_filing_number',
            'case_number',
            'is_draft',
            'status',
            'accepted_at',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'petitioner_vs_respondent',
        ]
        read_only_fields = [
            'id',
            'e_filing_number',
            'case_number',
            'status',
            'accepted_at',
            'created_at',
            'updated_at',
            'petitioner_vs_respondent',
        ]

    def get_petitioner_vs_respondent(self, obj):
        preferred = str(getattr(obj, "petitioner_name", None) or "").strip()
        if preferred:
            return preferred
        return build_petitioner_vs_respondent(
            obj,
            fallback_petitioner_name=getattr(obj, "petitioner_name", None) or "",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['case_type'] = (
            EfilingCaseTypeSerializer(instance.case_type).data
            if instance.case_type_id
            else None
        )
        return data
