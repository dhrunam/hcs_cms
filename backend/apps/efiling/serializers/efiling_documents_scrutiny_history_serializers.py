from rest_framework import serializers

from apps.core.models import EfilingDocumentsScrutinyHistory


class EfilingDocumentsScrutinyHistorySerializer(serializers.ModelSerializer):
    document_index_id = serializers.SerializerMethodField()
    document_id = serializers.SerializerMethodField()
    e_filing_id = serializers.SerializerMethodField()

    class Meta:
        model = EfilingDocumentsScrutinyHistory
        fields = [
            "id",
            "document_index_id",
            "document_id",
            "e_filing_id",
            "is_compliant",
            "comments",
            "scrutiny_status",
            "recieved_at",
            "response_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_document_index_id(self, obj):
        return obj.efiling_document_index_id

    def get_document_id(self, obj):
        if obj.efiling_document_index and obj.efiling_document_index.document_id:
            return obj.efiling_document_index.document_id
        return None

    def get_e_filing_id(self, obj):
        if (
            obj.efiling_document_index
            and obj.efiling_document_index.document
            and obj.efiling_document_index.document.e_filing_id
        ):
            return obj.efiling_document_index.document.e_filing_id
        return None
