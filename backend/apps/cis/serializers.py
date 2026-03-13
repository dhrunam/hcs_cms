from rest_framework import serializers

# from .models import CISFilingNumber, CISDataLog


# class CISFilingNumberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CISFilingNumber
#         fields = [
#             "id",
#             "case_number",
#             "case_title",
#             "case_type",
#             "petitioner",
#             "respondent",
#             "filing_date",
#             "created_at",
#         ]
#         read_only_fields = ["id", "created_at"]


# class CISDataLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CISDataLog
#         fields = [
#             "id",
#             "operation",
#             "status",
#             "source_case_id",
#             "target_case_number",
#             "payload",
#             "response",
#             "error_message",
#             "timestamp",
#         ]
#         read_only_fields = [
#             "id",
#             "timestamp",
#         ]
