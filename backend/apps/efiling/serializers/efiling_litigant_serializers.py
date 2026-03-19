from rest_framework import serializers

from apps.core.models import District, EfilingLitigant, OrgnameT, State


class EfilingOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgnameT
        fields = ['id', 'orgname']


class EfilingStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'state']


class EfilingDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'district']


class EfilingLitigantSerializer(serializers.ModelSerializer):
    organization_detail = EfilingOrganizationSerializer(source='organization', read_only=True)
    state_detail = EfilingStateSerializer(source='state_id', read_only=True)
    district_detail = EfilingDistrictSerializer(source='district_id', read_only=True)

    class Meta:
        model = EfilingLitigant
        fields = [
            'id',
            'e_filing',
            'e_filing_number',
            'organization',
            'sequence_number',
            'name',
            'gender',
            'age',
            'is_diffentially_abled',
            'contact',
            'is_petitioner',
            'sequence_number',
            'email',
            'religion',
            'caste',
            'occupation',
            'address',
            'state_id',
            'district_id',
            'organization_detail',
            'state_detail',
            'district_detail',
            'taluka',
            'village',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
