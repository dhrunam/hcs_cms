from rest_framework import serializers

from apps.core.models import Efiling


class EfilingSerializer(serializers.ModelSerializer):
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
