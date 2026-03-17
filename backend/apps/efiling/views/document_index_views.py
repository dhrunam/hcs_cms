from rest_framework import generics
from apps.core.models import DocumentIndex
from apps.efiling.serializers.document_index_serializers import DocumentIndexSerializer

class DocumentIndexListCreateView(generics.ListCreateAPIView):
   
    serializer_class = DocumentIndexSerializer
    def get_queryset(self):
        qs = DocumentIndex.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs
class DocumentIndexRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = DocumentIndexSerializer
    def get_queryset(self):
        qs = DocumentIndex.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs