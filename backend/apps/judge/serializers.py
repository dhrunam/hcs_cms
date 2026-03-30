from __future__ import annotations

from rest_framework import serializers

from apps.core.models import EfilingDocumentsIndex

from .models import (
    CourtroomDocumentAnnotation,
    CourtroomForward,
    CourtroomJudgeDecision,
)


class CourtroomForwardEntrySerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()


class CourtroomForwardSerializer(serializers.Serializer):
    forwarded_for_date = serializers.DateField()
    bench_key = serializers.CharField(max_length=50)
    listing_summary = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    document_index_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    efiling_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )


class CourtroomPendingCaseSerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    case_number = serializers.CharField(allow_null=True)
    bench_key = serializers.CharField()


class CourtroomDocumentAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtroomDocumentAnnotation
        fields = ["efiling_document_index", "annotation_text"]


class CourtroomCaseDocumentAnnotationUpsertSerializer(serializers.Serializer):
    efiling_document_index_id = serializers.IntegerField()
    annotation_text = serializers.CharField(allow_blank=True, required=False, allow_null=True)


class CourtroomDecisionSerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    forwarded_for_date = serializers.DateField()
    listing_date = serializers.DateField()
    status = serializers.ChoiceField(choices=CourtroomJudgeDecision.DecisionStatus.choices)
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

