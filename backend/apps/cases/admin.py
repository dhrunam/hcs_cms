from django.contrib import admin

# from .models import Case


# @admin.register(Case)
# class CaseAdmin(admin.ModelAdmin):
#     """Admin configuration for the Case model."""

#     list_display = [
#         "case_number",
#         "case_type",
#         "case_title",
#         "petitioner_name",
#         "respondent_name",
#         "filed_date",
#         "status",
#         "judge_name",
#         "created_by",
#         "created_at",
#     ]
#     list_filter = ["case_type", "status", "filed_date"]
#     search_fields = [
#         "case_number",
#         "case_title",
#         "petitioner_name",
#         "respondent_name",
#         "judge_name",
#     ]
#     readonly_fields = ["created_at", "updated_at"]
#     ordering = ["-filed_date"]
#     date_hierarchy = "filed_date"
#     fieldsets = (
#         (
#             "Case Identification",
#             {
#                 "fields": ("case_number", "case_type", "case_title"),
#             },
#         ),
#         (
#             "Parties",
#             {
#                 "fields": ("petitioner_name", "respondent_name"),
#             },
#         ),
#         (
#             "Court Details",
#             {
#                 "fields": ("filed_date", "status", "bench", "judge_name"),
#             },
#         ),
#         (
#             "Additional Information",
#             {
#                 "fields": ("description", "created_by"),
#             },
#         ),
#         (
#             "Timestamps",
#             {
#                 "fields": ("created_at", "updated_at"),
#                 "classes": ("collapse",),
#             },
#         ),
#     )
