from __future__ import annotations

from rest_framework import serializers

from apps.core.models import EfilingDocumentsIndex

from .models import (
    CourtroomDocumentAnnotation,
    CourtroomJudgeDecision,
    CourtroomSharedView,
)



class CourtroomPendingCaseSerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    case_number = serializers.CharField(allow_null=True)
    bench_key = serializers.CharField()


class CourtroomDocumentAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtroomDocumentAnnotation
        fields = ["efiling_document_index", "annotation_text", "annotation_data"]


class CourtroomCaseDocumentAnnotationUpsertSerializer(serializers.Serializer):
    efiling_document_index_id = serializers.IntegerField()
    annotation_text = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    annotation_data = serializers.JSONField(required=False, allow_null=True)


class CourtroomDecisionSerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    forwarded_for_date = serializers.DateField()
    status = serializers.ChoiceField(
        choices=CourtroomJudgeDecision.DecisionStatus.choices,
        required=False,
        default=CourtroomJudgeDecision.DecisionStatus.APPROVED,
    )
    approved = serializers.BooleanField(required=False)
    decision_notes = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    requested_document_index_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    def validate(self, attrs):
        status = attrs.get("status")
        requested_ids = attrs.get("requested_document_index_ids") or []
        if status == CourtroomJudgeDecision.DecisionStatus.REQUESTED_DOCS and not requested_ids:
            raise serializers.ValidationError(
                {"requested_document_index_ids": "At least one requested document is required."}
            )
        return attrs


class CourtroomSharedViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtroomSharedView
        fields = ["efiling_id", "document_index_id", "page_index", "is_active"]
