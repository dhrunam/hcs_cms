from django.contrib import admin



# @admin.register(CISFilingNumber)
# class CISFilingNumberAdmin(admin.ModelAdmin):
#     list_display = [
#         "case_number",
#         "case_title",
#         "case_type",
#         "petitioner",
#         "respondent",
#         "filing_date",
#         "created_at",
#     ]
#     list_filter = ["case_type", "created_at"]
#     search_fields = ["case_number", "case_title", "petitioner", "respondent"]
#     readonly_fields = ["created_at"]


# @admin.register(CISDataLog)
# class CISDataLogAdmin(admin.ModelAdmin):
#     list_display = ["operation", "status", "source_case_id", "target_case_number", "timestamp"]
#     list_filter = ["status", "operation", "timestamp"]
#     search_fields = ["source_case_id", "target_case_number"]
#     readonly_fields = ["timestamp", "payload", "response", "error_message"]
