from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingDocumentsIndex
from apps.efiling.serializers.efiling_document_index import (
    EfilingDocumentsIndexSerializer,
)


class EfilingDocumentsIndexListCreateView(ListCreateAPIView):
    
    serializer_class = EfilingDocumentsIndexSerializer
    def get_queryset(self):
        qs = EfilingDocumentsIndex.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs


class EfilingDocumentsIndexRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = EfilingDocumentsIndexSerializer
    def get_queryset(self):
        qs = EfilingDocumentsIndex.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

