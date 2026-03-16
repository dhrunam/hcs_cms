from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingDocuments
from apps.efiling.serializers.efiling_documents_serializers import (
    EfilingDocumentsSerializer,
)


class EfilingDocumentsListCreateView(ListCreateAPIView):
   
    serializer_class = EfilingDocumentsSerializer
    def get_queryset(self):
        qs = EfilingDocuments.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

class EfilingDocumentsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
   
    serializer_class = EfilingDocumentsSerializer

    def get_queryset(self):
        qs = EfilingDocuments.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs