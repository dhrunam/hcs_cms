from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingDocuments
from apps.efiling.serializers.efiling_documents_serializers import (
    EfilingDocumentsSerializer,
)
from apps.efiling.review_utils import can_replace_document, derive_filing_status, sync_document_index_for_upload


class EfilingDocumentsListCreateView(ListCreateAPIView):
   
    serializer_class = EfilingDocumentsSerializer
    def get_queryset(self):
        qs = EfilingDocuments.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        efiling_id = self.request.query_params.get('efiling_id')
        if efiling_id is not None:
            qs = qs.filter(e_filing=efiling_id)
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

    def perform_create(self, serializer):
        document = serializer.save()
        sync_document_index_for_upload(document, user=self.request.user if self.request.user.is_authenticated else None)
        derive_filing_status(document.e_filing)

class EfilingDocumentsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
   
    serializer_class = EfilingDocumentsSerializer

    def get_queryset(self):
        qs = EfilingDocuments.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

    def partial_update(self, request, *args, **kwargs):
        return self._save_document_update(request, *args, partial=True, **kwargs)

    def update(self, request, *args, **kwargs):
        return self._save_document_update(request, *args, partial=False, **kwargs)

    def _save_document_update(self, request, *args, partial=False, **kwargs):
        document = self.get_object()
        is_file_replacement = "final_document" in request.FILES or "final_document" in request.data

        if is_file_replacement and not can_replace_document(document):
            raise ValidationError(
                {
                    "final_document": (
                        "This document can only be replaced after the scrutiny officer rejects it."
                    )
                }
            )

        kwargs["partial"] = partial
        response = super().update(request, *args, **kwargs)
        document.refresh_from_db()
        if is_file_replacement:
            sync_document_index_for_upload(
                document,
                user=request.user if request.user.is_authenticated else None,
            )
        derive_filing_status(document.e_filing)
        return response