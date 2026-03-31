from __future__ import annotations

from django.urls import path

from apps.judge.views import (
    CourtroomDecisionCalendarView,
    CourtroomApprovedLookupView,
    CourtroomCaseSummaryView,
    CourtroomCaseDocumentsView,
    CourtroomDecisionView,
    CourtroomDocumentAnnotationView,
    CourtroomForwardView,
    CourtroomPendingCasesView,
)

app_name = "judge"

urlpatterns = [
    path("courtroom/forward/", CourtroomForwardView.as_view(), name="courtroom-forward"),
    path(
        "courtroom/pending/",
        CourtroomPendingCasesView.as_view(),
        name="courtroom-pending",
    ),
    path(
        "courtroom/cases/<int:efiling_id>/summary/",
        CourtroomCaseSummaryView.as_view(),
        name="courtroom-case-summary",
    ),
    path(
        "courtroom/cases/<int:efiling_id>/documents/",
        CourtroomCaseDocumentsView.as_view(),
        name="courtroom-case-documents",
    ),
    path(
        "courtroom/document-annotations/",
        CourtroomDocumentAnnotationView.as_view(),
        name="courtroom-document-annotations",
    ),
    path(
        "courtroom/decisions/",
        CourtroomDecisionView.as_view(),
        name="courtroom-decisions",
    ),
    path(
        "courtroom/approved/",
        CourtroomApprovedLookupView.as_view(),
        name="courtroom-approved-lookup",
    ),
    path(
        "courtroom/decisions/calendar/",
        CourtroomDecisionCalendarView.as_view(),
        name="courtroom-decisions-calendar",
    ),
]

