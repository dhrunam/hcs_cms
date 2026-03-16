from rest_framework import generics
from apps.core.models import DocumentIndex
from apps.efiling.serializers.document_index_serializers import DocumentIndexSerializer

class DocumentIndexListCreateView(generics.ListCreateAPIView):
    queryset = DocumentIndex.objects.all()
    serializer_class = DocumentIndexSerializer

class DocumentIndexRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentIndex.objects.all()
    serializer_class = DocumentIndexSerializer
