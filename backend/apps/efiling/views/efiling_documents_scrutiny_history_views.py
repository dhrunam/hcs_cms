from rest_framework.generics import ListAPIView

from apps.core.models import EfilingDocumentsScrutinyHistory
from apps.efiling.serializers.efiling_documents_scrutiny_history_serializers import (
    EfilingDocumentsScrutinyHistorySerializer,
)


class EfilingDocumentsScrutinyHistoryListView(ListAPIView):
    serializer_class = EfilingDocumentsScrutinyHistorySerializer

    def get_queryset(self):
        qs = (
            EfilingDocumentsScrutinyHistory.objects.select_related(
                "efiling_document_index",
                "efiling_document_index__document",
                "efiling_document_index__document__e_filing",
            )
            .all()
            .order_by("-recieved_at", "-id")
        )
        document_index_id = self.request.query_params.get("document_index_id")
        document_id = self.request.query_params.get("document_id")
        efiling_id = self.request.query_params.get("efiling_id")

        if document_index_id is not None:
            qs = qs.filter(efiling_document_index=document_index_id)
        if document_id is not None:
            qs = qs.filter(efiling_document_index__document=document_id)
        if efiling_id is not None:
            qs = qs.filter(efiling_document_index__document__e_filing=efiling_id)
        return qs
