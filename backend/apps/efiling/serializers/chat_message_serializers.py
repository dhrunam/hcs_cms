from rest_framework import serializers

from apps.core.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.SerializerMethodField()
    sender_role = serializers.SerializerMethodField()
    is_current_user = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "e_filing",
            "sender",
            "sender_name",
            "sender_email",
            "sender_role",
            "message",
            "created_at",
            "updated_at",
            "is_current_user",
        ]
        read_only_fields = [
            "id",
            "e_filing",
            "sender",
            "sender_name",
            "sender_email",
            "sender_role",
            "created_at",
            "updated_at",
            "is_current_user",
        ]

    def validate_message(self, value):
        message = (value or "").strip()
        if not message:
            raise serializers.ValidationError("Message cannot be empty.")
        return message

    def get_sender_name(self, obj):
        if not obj.sender:
            return "System"
        full_name = obj.sender.get_full_name().strip()
        return full_name or obj.sender.username or obj.sender.email

    def get_sender_email(self, obj):
        return obj.sender.email if obj.sender else None

    def get_sender_role(self, obj):
        if not obj.sender:
            return "system"

        group_names = {
            str(name).strip().upper()
            for name in obj.sender.groups.values_list("name", flat=True)
            if str(name).strip()
        }

        if any("SCRUTINY" in name for name in group_names):
            return "scrutiny_officer"
        if any("ADVOCATE" in name for name in group_names):
            return "advocate"

        designation = str(getattr(obj.sender, "designation", "") or "").strip().lower()
        if "scrutiny" in designation:
            return "scrutiny_officer"
        if "advocate" in designation:
            return "advocate"

        return "user"

    def get_is_current_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not obj.sender_id:
            return False
        return obj.sender_id == request.user.id
