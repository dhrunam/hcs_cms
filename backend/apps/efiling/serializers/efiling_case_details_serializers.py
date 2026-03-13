from rest_framework import serializers

from apps.core.models import EfilingCaseDetails


class EfilingCaseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EfilingCaseDetails
        fields = [
            'id',
            'e_filing',
            'e_filing_number',
            'cause_of_action',
            'date_of_cause_of_action',
            'dispute_state',
            'dispute_district',
            'dispute_taluka',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
