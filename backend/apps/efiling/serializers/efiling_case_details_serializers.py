from rest_framework import serializers

from apps.core.models import District, EfilingCaseDetails, State


class EfilingDisputeStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["id", "state"]


class EfilingDisputeDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "district"]


class EfilingCaseDetailsSerializer(serializers.ModelSerializer):
    dispute_state = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(),
        required=False,
        allow_null=True,
    )
    dispute_district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = EfilingCaseDetails
        fields = [
            "id",
            "e_filing",
            "e_filing_number",
            "cause_of_action",
            "date_of_cause_of_action",
            "dispute_state",
            "dispute_district",
            "dispute_taluka",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["dispute_state"] = (
            EfilingDisputeStateSerializer(instance.dispute_state).data
            if instance.dispute_state_id
            else None
        )
        data["dispute_district"] = (
            EfilingDisputeDistrictSerializer(instance.dispute_district).data
            if instance.dispute_district_id
            else None
        )
        return data
