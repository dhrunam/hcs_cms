from django.urls import path
from .views import (
    RegisteredCasesListView,
    AssignBenchesView,
    CourtroomForwardView,
    ReaderApprovedCasesView,
    ReaderAssignDateView,
    ReaderResetBenchView,
)

app_name = "reader"

urlpatterns = [
    path("registered-cases/", RegisteredCasesListView.as_view(), name="registered-cases"),
    path("assign-bench/", AssignBenchesView.as_view(), name="assign-bench"),
    path("forward/", CourtroomForwardView.as_view(), name="forward"),
    path("approved-cases/", ReaderApprovedCasesView.as_view(), name="approved-cases"),
    path("assign-date/", ReaderAssignDateView.as_view(), name="assign-date"),
    path("reset-bench/", ReaderResetBenchView.as_view(), name="reset-bench"),
]
