from __future__ import annotations

from rest_framework import serializers


class CourtroomForwardSerializer(serializers.Serializer):
    forwarded_for_date = serializers.DateField()
    bench_key = serializers.CharField(max_length=50)
    listing_summary = serializers.CharField(
        allow_blank=True,
        required=False,
        allow_null=True,
    )
    document_index_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    efiling_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class AssignBenchEntrySerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    bench_key = serializers.CharField(max_length=50)


class AssignBenchesSerializer(serializers.Serializer):
    assignments = AssignBenchEntrySerializer(many=True)


class BenchConfigurationSerializer(serializers.Serializer):
    bench_key = serializers.CharField()
    label = serializers.CharField()
    bench_code = serializers.CharField(allow_null=True)
    bench_name = serializers.CharField(allow_null=True)
    judge_names = serializers.ListField(child=serializers.CharField())
    judge_user_ids = serializers.ListField(child=serializers.IntegerField())
    reader_user_ids = serializers.ListField(child=serializers.IntegerField())
    is_accessible_to_reader = serializers.BooleanField()


class ReaderDailyProceedingSubmitSerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    hearing_date = serializers.DateField()
    next_listing_date = serializers.DateField()
    proceedings_text = serializers.CharField(allow_blank=False)
    steno_purpose_code = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    reader_remark = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    steno_remark = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    listing_remark = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    document_type = serializers.ChoiceField(
        choices=[("ORDER", "Order"), ("JUDGMENT", "Judgment")],
        required=False,
        default="ORDER",
    )


class StenoDraftUploadSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    draft_document_index_id = serializers.IntegerField()


class StenoSubmitForJudgeSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()


class StenoResolveAnnotationSerializer(serializers.Serializer):
    annotation_id = serializers.IntegerField()
