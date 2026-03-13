from rest_framework import serializers

from apps.core.models import EfilingLitigant


class EfilingLitigantSerializer(serializers.ModelSerializer):
    class Meta:
        model = EfilingLitigant
        fields = [
            'id',
            'e_filing',
            'e_filing_number',
            'name',
            'gender',
            'age',
            'is_diffentially_abled',
            'contact',
            'is_petitioner',
            'email',
            'religion',
            'caste',
            'occupation',
            'address',
            'state_id',
            'district_id',
            'taluka',
            'village',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
