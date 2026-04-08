from django.urls import path
from .views import (
    RegisteredCasesListView,
    AssignBenchesView,
    BenchConfigurationsView,
    CourtroomForwardView,
    ReaderApprovedCasesView,
    ReaderAssignDateView,
    ReaderResetBenchView,
    ReaderDailyProceedingsListView,
    ReaderDailyProceedingsSubmitView,
    StenoQueueListView,
    StenoDraftUploadView,
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
    path("reset-bench/", ReaderResetBenchView.as_view(), name="reset-bench"),
    path("daily-proceedings/", ReaderDailyProceedingsListView.as_view(), name="daily-proceedings"),
    path("daily-proceedings/submit/", ReaderDailyProceedingsSubmitView.as_view(), name="daily-proceedings-submit"),
    path("steno/queue/", StenoQueueListView.as_view(), name="steno-queue"),
    path("steno/upload-draft/", StenoDraftUploadView.as_view(), name="steno-upload-draft"),
    path("steno/submit-judge/", StenoSubmitForJudgeApprovalView.as_view(), name="steno-submit-judge"),
]
