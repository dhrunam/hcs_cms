from rest_framework import serializers

from apps.core.models import ActT, EfilingActs


class EfilingActTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActT
        fields = ["actcode", "actname"]


class EfilingActsSerializer(serializers.ModelSerializer):
    act = serializers.PrimaryKeyRelatedField(
        queryset=ActT.objects.all(),
        required=False,
        allow_null=True,
    )

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["act"] = EfilingActTSerializer(instance.act).data if instance.act_id else None
        return data
