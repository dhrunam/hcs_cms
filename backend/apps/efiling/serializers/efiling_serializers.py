from rest_framework import serializers

from apps.core.models import CaseTypeT, Efiling


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

    class Meta:
        model = Efiling
        fields = [
            'id',
            'case_type',
            'bench',
            'petitioner_name',
            'petitioner_contact',
            'e_filing_number',
            'is_draft',
            'status',
            'accepted_at',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['case_type'] = (
            EfilingCaseTypeSerializer(instance.case_type).data
            if instance.case_type_id
            else None
        )
        return data
