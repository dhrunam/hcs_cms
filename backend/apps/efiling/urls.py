from django.urls import path

from apps.efiling.views.efiling_acts_views import (
    EfilingActsListCreateView,
    EfilingActsRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_case_details_views import (
    EfilingCaseDetailsListCreateView,
    EfilingCaseDetailsRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_litigant_views import (
    EfilingLitigantListCreateView,
    EfilingLitigantRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_views import (
    EfilingListCreateView,
    EfilingRetrieveUpdateDestroyView,
    EfilingSubmitApprovedView,
)
from apps.efiling.views.document_index_views import (
    DocumentIndexListCreateView,
    DocumentIndexRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_documents_views import (
    EfilingDocumentsListCreateView,
    EfilingDocumentsRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_documents_index_views import (
    EfilingDocumentsIndexListCreateView,
    EfilingDocumentsIndexRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_documents_scrutiny_history_views import (
    EfilingDocumentsScrutinyHistoryListView,
)
from apps.efiling.views.ia_views import (
    IAListCreateView,
    IARetrieveUpdateDestroyView,
)
from apps.efiling.views.ia_acts_views import (
    IAActsListCreateView,
    IAActsRetrieveUpdateDestroyView,
)
from apps.efiling.views.efiling_file_scrutiny_checklist_view import (
    FileScrutinyCheckListListCreateView,
    FileScrutinyCheckListRetrieveUpdateDestroyView,
)
from apps.efiling.views.vakalatnama_views import (
    VakalatnamaListCreateView
    ,VakalatnamaRetrieveUpdateDestroyView)
from apps.efiling.views.efiler_document_access_views import (
    EfilerDocumentAccessListCreateView,
    EfilerDocumentAccessRetrieveUpdateDestroyView,
)
from apps.efiling.views.advocate_views import (
    AdvocateListView,
    AdvocateRetrieveView,
)
from apps.efiling.views.pdf_merge_views import merge_pdfs
from apps.efiling.views.notification_views import EfilingNotificationListView
from apps.efiling.views.document_stream_views import EfilingDocumentStreamByIndexView


app_name = "efiling"

urlpatterns = [
    path("advocates/", AdvocateListView.as_view(), name="advocate-list"),
    path("advocates/<int:adv_code>/", AdvocateRetrieveView.as_view(), name="advocate-detail"),
    path("efilings/", EfilingListCreateView.as_view(), name="efiling-list-create"),
    path(
        "efilings/<int:pk>/",
        EfilingRetrieveUpdateDestroyView.as_view(),
        name="efiling-detail",
    ),
    path(
        "efilings/<int:pk>/submit-approved/",
        EfilingSubmitApprovedView.as_view(),
        name="efiling-submit-approved",
    ),
    path(
        "ias/",
        IAListCreateView.as_view(),
        name="ia-list-create",
    ),
    path(
        "ias/<int:pk>/",
        IARetrieveUpdateDestroyView.as_view(),
        name="ia-detail",
    ),
    path(
        "ia-acts/",
        IAActsListCreateView.as_view(),
        name="ia-acts-list-create",
    ),
    path(
        "ia-acts/<int:pk>/",
        IAActsRetrieveUpdateDestroyView.as_view(),
        name="ia-acts-detail",
    ),
    path(
        "efiling-litigants/",
        EfilingLitigantListCreateView.as_view(),
        name="efiling-litigant-list-create",
    ),
    path(
        "efiling-litigants/<int:pk>/",
        EfilingLitigantRetrieveUpdateDestroyView.as_view(),
        name="efiling-litigant-detail",
    ),
    path(
        "efiling-case-details/",
        EfilingCaseDetailsListCreateView.as_view(),
        name="efiling-case-details-list-create",
    ),
    path(
        "efiling-case-details/<int:pk>/",
        EfilingCaseDetailsRetrieveUpdateDestroyView.as_view(),
        name="efiling-case-details-detail",
    ),
    path(
        "efiling-acts/",
        EfilingActsListCreateView.as_view(),
        name="efiling-acts-list-create",
    ),
    path(
        "efiling-acts/<int:pk>/",
        EfilingActsRetrieveUpdateDestroyView.as_view(),
        name="efiling-acts-detail",
    ),
    path(
        "document-index/",
        DocumentIndexListCreateView.as_view(),
        name="document-index-list-create",
    ),
    path(
        "document-index/<int:pk>/",
        DocumentIndexRetrieveUpdateDestroyView.as_view(),
        name="document-index-detail",
    ),
    path(
        "efiling-documents/",
        EfilingDocumentsListCreateView.as_view(),
        name="efiling-documents-list-create",
    ),
    path(
        "efiling-documents/<int:pk>/",
        EfilingDocumentsRetrieveUpdateDestroyView.as_view(),
        name="efiling-documents-detail",
    ),
    path(
        "efiling-documents-index/",
        EfilingDocumentsIndexListCreateView.as_view(),
        name="efiling-documents-index-list-create",
    ),
    path(
        "efiling-documents-index/<int:pk>/",
        EfilingDocumentsIndexRetrieveUpdateDestroyView.as_view(),
        name="efiling-documents-index-detail",
    ),
    path(
        "efiling-documents-scrutiny-history/",
        EfilingDocumentsScrutinyHistoryListView.as_view(),
        name="efiling-documents-scrutiny-history-list",
    ),
    path(
        "file-scrutiny-checklists/",
        FileScrutinyCheckListListCreateView.as_view(),
        name="file-scrutiny-checklist-list-create",
    ),
    path(
        "file-scrutiny-checklists/<int:pk>/",
        FileScrutinyCheckListRetrieveUpdateDestroyView.as_view(),
        name="file-scrutiny-checklist-detail",
    ),
    path(
        "vakalatnama/",
        VakalatnamaListCreateView.as_view(),
        name="vakalatnama-list-create",
    ),
    path(
        "vakalatnama/<int:pk>/",
        VakalatnamaRetrieveUpdateDestroyView.as_view(),
        name="vakalatnama-detail",
    ),
    path(
        "efiler-document-access/",
        EfilerDocumentAccessListCreateView.as_view(),
        name="efiler-document-access-list-create",
    ),
    path(
        "efiler-document-access/<int:pk>/",
        EfilerDocumentAccessRetrieveUpdateDestroyView.as_view(),
        name="efiler-document-access-detail",
    ),
    path("merge-pdfs/", merge_pdfs, name="merge-pdfs"),
    path("notifications/", EfilingNotificationListView.as_view(), name="notification-list"),
    path(
        "efiling-documents-index/<int:document_index_id>/stream/",
        EfilingDocumentStreamByIndexView.as_view(),
        name="efiling-document-index-stream",
    ),
]

