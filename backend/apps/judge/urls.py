from __future__ import annotations

from django.urls import path

from apps.judge.views import (
    CourtroomDecisionCalendarView,
    CourtroomApprovedLookupView,
    CourtroomCaseSummaryView,
    CourtroomCaseDocumentsView,
    CourtroomDecisionView,
    CourtroomDocumentAnnotationView,
    CourtroomPendingCasesView,
    CourtroomSharedViewAPIView,
    JudgeStenoWorkflowListView,
    JudgeStenoWorkflowAnnotationView,
    JudgeStenoWorkflowAnnotationsSnapshotView,
    JudgeStenoWorkflowDecisionView,
)

app_name = "judge"

urlpatterns = [

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
    path(
        "courtroom/shares/",
        CourtroomSharedViewAPIView.as_view(),
        name="courtroom-shares",
    ),
    path(
        "steno-workflows/",
        JudgeStenoWorkflowListView.as_view(),
        name="judge-steno-workflows",
    ),
    path(
        "steno-workflows/annotations/",
        JudgeStenoWorkflowAnnotationView.as_view(),
        name="judge-steno-workflow-annotations",
    ),
    path(
        "steno-workflows/annotations/snapshot/",
        JudgeStenoWorkflowAnnotationsSnapshotView.as_view(),
        name="judge-steno-workflow-annotations-snapshot",
    ),
    path(
        "steno-workflows/decision/",
        JudgeStenoWorkflowDecisionView.as_view(),
        name="judge-steno-workflow-decision",
    ),

]

