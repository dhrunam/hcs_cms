from rest_framework import serializers

from apps.core.models import EfilingDocuments, EfilingDocumentsIndex
from apps.efiling.pdf_validators import validate_pdf_file

_ALLOWED_FILED_BY = frozenset({"PETITIONER", "RESPONDENT", "APPELLANT"})


class EfilingDocumentsSerializer(serializers.ModelSerializer):
    """
    Serializer for top-level efiling documents (EfilingDocuments).
    """

    can_replace = serializers.SerializerMethodField()
    scrutiny_status = serializers.SerializerMethodField()
    is_new_for_scrutiny = serializers.SerializerMethodField()

    class Meta:
        model = EfilingDocuments
        fields = [
            "id",
            "e_filing",
            "e_filing_number",
            "ia_number",
            "document_type",
            "parent_e_filing_document",
            "final_document",
            "can_replace",
            "scrutiny_status",
            "is_new_for_scrutiny",
            "is_ia",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "filed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_document_index(self, obj):
        return (
            EfilingDocumentsIndex.objects.filter(document=obj, is_active=True)
            .order_by("id")
            .first()
        )

    def get_can_replace(self, obj):
        if obj.e_filing and obj.e_filing.is_draft:
            return True

        document_index = self.get_document_index(obj)
        return bool(
            document_index
            and document_index.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.REJECTED
        )

    def get_scrutiny_status(self, obj):
        document_index = self.get_document_index(obj)
        return document_index.scrutiny_status if document_index else None

    def get_is_new_for_scrutiny(self, obj):
        document_index = self.get_document_index(obj)
        return document_index.is_new_for_scrutiny if document_index else False

    def validate_final_document(self, value):
        if value:
            validate_pdf_file(value, "final_document")
        return value

    def validate_filed_by(self, value):
        if value in (None, ""):
            return value
        normalized = str(value).strip().upper()
        if normalized not in _ALLOWED_FILED_BY:
            raise serializers.ValidationError(
                "filed_by must be one of: PETITIONER, RESPONDENT, APPELLANT."
            )
        return normalized
