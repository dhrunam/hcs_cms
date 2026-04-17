from rest_framework import serializers

from apps.core.models import CaseTypeT, Efiling
from apps.efiling.party_display import build_petitioner_vs_respondent


class EfilingCaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseTypeT
        fields = ['id', 'case_type', 'type_name', 'full_form', 'annexure_type']


class EfilingSerializer(serializers.ModelSerializer):
    case_type = serializers.PrimaryKeyRelatedField(
        queryset=CaseTypeT.objects.all(),
        required=False,
        allow_null=True,
    )
    petitioner_vs_respondent = serializers.SerializerMethodField(read_only=True)
    latest_chat_message_id = serializers.SerializerMethodField(read_only=True)
    latest_chat_message_at = serializers.SerializerMethodField(read_only=True)
    latest_chat_is_from_current_user = serializers.SerializerMethodField(read_only=True)

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
            'latest_chat_message_id',
            'latest_chat_message_at',
            'latest_chat_is_from_current_user',
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
            'latest_chat_message_id',
            'latest_chat_message_at',
            'latest_chat_is_from_current_user',
        ]

    def get_petitioner_vs_respondent(self, obj):
        preferred = str(getattr(obj, "petitioner_name", None) or "").strip()
        if preferred:
            return preferred
        return build_petitioner_vs_respondent(
            obj,
            fallback_petitioner_name=getattr(obj, "petitioner_name", None) or "",
        )

    def get_latest_chat_message_id(self, obj):
        latest_message = obj.chat_messages.filter(is_active=True).order_by('-created_at', '-id').first()
        return latest_message.id if latest_message else None

    def get_latest_chat_message_at(self, obj):
        latest_message = obj.chat_messages.filter(is_active=True).order_by('-created_at', '-id').first()
        return latest_message.created_at if latest_message else None

    def get_latest_chat_is_from_current_user(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        latest_message = obj.chat_messages.filter(is_active=True).order_by('-created_at', '-id').first()
        if not latest_message or not latest_message.sender_id:
            return False
        return latest_message.sender_id == request.user.id

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['case_type'] = (
            EfilingCaseTypeSerializer(instance.case_type).data
            if instance.case_type_id
            else None
        )
        return data
