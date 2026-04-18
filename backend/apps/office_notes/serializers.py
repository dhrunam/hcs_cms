from rest_framework import serializers

from .models import OfficeNote


class OfficeNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OfficeNote
        fields = [
            "id",
            "efiling",
            "note_content",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_created_by_name(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name().strip()
            return full_name if full_name else obj.created_by.email
        return "Unknown"