from rest_framework import serializers

from apps.core.models import EfilingActs


class EfilingActsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EfilingActs
        fields = [
            'id',
            'e_filing',
            'e_filing_number',
            'act',
            'section',
            'sub_section',
            'description',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
