from rest_framework import serializers


class CauseListDraftEntrySerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    serial_no = serializers.IntegerField(required=False, allow_null=True)
    included = serializers.BooleanField(default=True)
    petitioner_advocate = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    respondent_advocate = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    selected_ias = serializers.ListField(child=serializers.JSONField(), required=False, allow_empty=True)


class CauseListDraftSaveSerializer(serializers.Serializer):
    cause_list_date = serializers.DateField()
    bench_key = serializers.CharField(max_length=50)
    entries = CauseListDraftEntrySerializer(many=True)


class CauseListPublishSerializer(serializers.Serializer):
    """
    Publish in one step (no draft UI): accepts the same structure as draft-save.
    """

    cause_list_date = serializers.DateField()
    bench_key = serializers.CharField(max_length=50)
    entries = CauseListDraftEntrySerializer(many=True)


class CauseListPublishedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    bench_key = serializers.CharField()
    pdf_url = serializers.CharField(allow_null=True, required=False)


class AssignBenchEntrySerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    bench_key = serializers.CharField(max_length=50)


class AssignBenchesSerializer(serializers.Serializer):
    assignments = AssignBenchEntrySerializer(many=True)


class LatestCauseListLookupSerializer(serializers.Serializer):
    case_numbers = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


class NextCauseListLookupSerializer(serializers.Serializer):
    case_numbers = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


