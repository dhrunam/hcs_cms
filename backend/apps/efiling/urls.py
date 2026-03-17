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
from apps.efiling.views.ia_views import (
    IAListCreateView,
    IARetrieveUpdateDestroyView,
)


app_name = "efiling"

urlpatterns = [
    path("efilings/", EfilingListCreateView.as_view(), name="efiling-list-create"),
    path(
        "efilings/<int:pk>/",
        EfilingRetrieveUpdateDestroyView.as_view(),
        name="efiling-detail",
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
]

