from rest_framework import serializers

from apps.core.models import EfilingDocuments


class EfilingDocumentsSerializer(serializers.ModelSerializer):
    """
    Serializer for top-level efiling documents (EfilingDocuments).
    """

    class Meta:
        model = EfilingDocuments
        fields = [
            "id",
            "e_filing",
            "e_filing_number",
            "document_type",
            "parent_e_filing_document",
            "is_ia",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

