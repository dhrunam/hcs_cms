from django.urls import path
from .views import (
    RegisteredCasesListView,
    AssignBenchesView,
    BenchConfigurationsView,
    CourtroomForwardView,
    ReaderCaseReallocationHistoryView,
    ReaderApprovedCasesView,
    ReaderAssignDateView,
    ReaderReallocateCaseView,
    ReaderReallocationOrderFileView,
    ReaderResetBenchView,
    ReaderDailyProceedingsListView,
    ReaderDailyProceedingsSubmitView,
    StenoQueueListView,
    StenoDraftFileUploadView,
    StenoDraftUploadView,
    StenoSignedUploadPublishView,
    StenoSubmitForJudgeApprovalView,
)

app_name = "reader"

urlpatterns = [
    path("bench-configurations/", BenchConfigurationsView.as_view(), name="bench-configurations"),
    path("registered-cases/", RegisteredCasesListView.as_view(), name="registered-cases"),
    path("assign-bench/", AssignBenchesView.as_view(), name="assign-bench"),
    path("forward/", CourtroomForwardView.as_view(), name="forward"),
    path("approved-cases/", ReaderApprovedCasesView.as_view(), name="approved-cases"),
    path("assign-date/", ReaderAssignDateView.as_view(), name="assign-date"),
    path("reallocate-case/", ReaderReallocateCaseView.as_view(), name="reallocate-case"),
    path("cases/<int:efiling_id>/reallocations/", ReaderCaseReallocationHistoryView.as_view(), name="case-reallocation-history"),
    path("reallocations/<int:reallocation_id>/order-file/", ReaderReallocationOrderFileView.as_view(), name="reallocation-order-file"),
    path("reset-bench/", ReaderResetBenchView.as_view(), name="reset-bench"),
    path("daily-proceedings/", ReaderDailyProceedingsListView.as_view(), name="daily-proceedings"),
    path("daily-proceedings/submit/", ReaderDailyProceedingsSubmitView.as_view(), name="daily-proceedings-submit"),
    path("steno/queue/", StenoQueueListView.as_view(), name="steno-queue"),
    path("steno/upload-draft-file/", StenoDraftFileUploadView.as_view(), name="steno-upload-draft-file"),
    path("steno/upload-draft/", StenoDraftUploadView.as_view(), name="steno-upload-draft"),
    path("steno/upload-signed-publish/", StenoSignedUploadPublishView.as_view(), name="steno-upload-signed-publish"),
    path("steno/submit-judge/", StenoSubmitForJudgeApprovalView.as_view(), name="steno-submit-judge"),
]
