from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilerDocumentAccess
from apps.efiling.serializers.efiler_document_access_serializers import EfilerDocumentAccessSerializer


class EfilerDocumentAccessListCreateView(ListCreateAPIView):
    queryset = EfilerDocumentAccess.objects.all()
    serializer_class = EfilerDocumentAccessSerializer
    def get_queryset(self):
        qs = EfilerDocumentAccess.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs


class EfilerDocumentAccessRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilerDocumentAccess.objects.all()
    serializer_class = EfilerDocumentAccessSerializer
    def get_queryset(self):
        qs = EfilerDocumentAccess.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs