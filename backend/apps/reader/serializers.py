from __future__ import annotations

from rest_framework import serializers

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

class AssignBenchEntrySerializer(serializers.Serializer):
    efiling_id = serializers.IntegerField()
    bench_key = serializers.CharField(max_length=50)

class AssignBenchesSerializer(serializers.Serializer):
    assignments = AssignBenchEntrySerializer(many=True)
