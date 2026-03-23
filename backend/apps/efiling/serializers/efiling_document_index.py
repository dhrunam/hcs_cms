from rest_framework import serializers

from apps.core.models import EfilingDocumentsIndex
from apps.efiling.pdf_validators import validate_pdf_file
from apps.efiling.review_utils import can_replace_document


class EfilingDocumentsIndexSerializer(serializers.ModelSerializer):
    """
    Serializer for individual document parts (EfilingDocumentsIndex).
    Exposes a read-only URL for the uploaded file.
    """

    file_url = serializers.SerializerMethodField()
    e_filing_id = serializers.SerializerMethodField()
    e_filing_number = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
    ia_number = serializers.SerializerMethodField()
    history_count = serializers.SerializerMethodField()
    can_replace = serializers.SerializerMethodField()

    class Meta:
        model = EfilingDocumentsIndex
        fields = [
            "id",
            "document",
            "index",
            "document_part_name",
            "file_part_path",
            "file_url",
            "is_locked",
            "document_sequence",
            "is_compliant",
            "comments",
            "scrutiny_status",
            "draft_scrutiny_status",
            "draft_comments",
            "draft_reviewed_at",
            "is_new_for_scrutiny",
            "last_resubmitted_at",
            "last_reviewed_at",
            "e_filing_id",
            "e_filing_number",
            "document_type",
            "ia_number",
            "history_count",
            "can_replace",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file_part_path and hasattr(obj.file_part_path, "url"):
            if request is not None:
                return request.build_absolute_uri(obj.file_part_path.url)
            return obj.file_part_path.url
        return None

    def get_e_filing_id(self, obj):
        return obj.document.e_filing_id if obj.document_id and obj.document else None

    def get_e_filing_number(self, obj):
        return obj.document.e_filing_number if obj.document_id and obj.document else None

    def get_document_type(self, obj):
        return obj.document.document_type if obj.document_id and obj.document else None

    def get_ia_number(self, obj):
        return obj.document.ia_number if obj.document_id and obj.document else None

    def get_history_count(self, obj):
        return obj.scrutiny_history.count()

    def get_can_replace(self, obj):
        if not obj.document_id or not obj.document:
            return False
        return can_replace_document(obj.document, document_index_id=obj.id)

    def validate_file_part_path(self, value):
        if value:
            validate_pdf_file(value, "file_part_path")
        return value

