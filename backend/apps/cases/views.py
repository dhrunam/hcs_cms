from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

# from .models import Case
from .serializers import CaseSerializer


class CaseViewSet(viewsets.ModelViewSet):
    pass
    # """
    # CRUD endpoints for Cases.

    # Supports filtering by ``status`` and ``case_type`` via query params,
    # free-text search on case number / title / petitioner / respondent,
    # and ordering on any field.

    # All endpoints require a valid OAuth2 bearer token.
    # """

    # serializer_class = CaseSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = [
    #     "case_number",
    #     "case_title",
    #     "petitioner_name",
    #     "respondent_name",
    #     "judge_name",
    # ]
    # ordering_fields = ["filed_date", "case_number", "status", "case_type", "created_at"]
    # ordering = ["-filed_date"]

    # def get_queryset(self):
    #     queryset = Case.objects.select_related("created_by").all()

    #     status = self.request.query_params.get("status")
    #     if status:
    #         queryset = queryset.filter(status=status.upper())

    #     case_type = self.request.query_params.get("case_type")
    #     if case_type:
    #         queryset = queryset.filter(case_type=case_type.upper())

    #     return queryset

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.request.user)