from django.urls import path

from apps.listing.views import (
    AssignBenchesView,
    RegisteredCasesListView,
    CauseListDraftPreviewView,
    CauseListDraftPdfPreviewView,
    CauseListDraftSaveView,
    CauseListEntryLookupByCaseNumberView,
    CauseListPublishView,
    CauseListPublishDirectView,
    PublishedCauseListByDateView,
    LatestPublishedCauseListsView,
    LatestPublishedCauseListLookupView,
    NextPublishedCauseListLookupView,
)

app_name = "listing"

urlpatterns = [
    path(
        "registered-cases/",
        RegisteredCasesListView.as_view(),
        name="registered-cases",
    ),
    path(
        "registered-cases/assign-bench/",
        AssignBenchesView.as_view(),
        name="assign-benches-singular",
    ),
    path(
        "registered-cases/assign-benches/",
        AssignBenchesView.as_view(),
        name="assign-benches",
    ),
    path(
        "cause-lists/draft/preview/",
        CauseListDraftPreviewView.as_view(),
        name="cause-list-draft-preview",
    ),
    path(
        "cause-lists/draft/pdf/",
        CauseListDraftPdfPreviewView.as_view(),
        name="cause-list-draft-pdf-preview",
    ),
    path(
        "cause-lists/draft/save/",
        CauseListDraftSaveView.as_view(),
        name="cause-list-draft-save",
    ),
    path(
        "cause-lists/<int:pk>/publish/",
        CauseListPublishView.as_view(),
        name="cause-list-publish",
    ),
    path(
        "cause-lists/publish/",
        CauseListPublishDirectView.as_view(),
        name="cause-list-publish-direct",
    ),
    path(
        "cause-lists/published/",
        PublishedCauseListByDateView.as_view(),
        name="published-cause-lists-by-date",
    ),
    path(
        "cause-lists/published/latest/",
        LatestPublishedCauseListsView.as_view(),
        name="latest-published-cause-lists",
    ),
    path(
        "cause-lists/published/latest/lookup/",
        LatestPublishedCauseListLookupView.as_view(),
        name="latest-published-cause-list-lookup",
    ),
    path(
        "cause-lists/published/next/lookup/",
        NextPublishedCauseListLookupView.as_view(),
        name="next-published-cause-list-lookup",
    ),
    path(
        "cause-lists/entry/",
        CauseListEntryLookupByCaseNumberView.as_view(),
        name="cause-list-entry-lookup-by-case-number",
    ),
]

