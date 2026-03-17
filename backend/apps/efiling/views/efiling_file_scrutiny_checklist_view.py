from rest_framework import generics
from apps.core.models import FileScrutinyCheckList
from apps.efiling.serializers.efiling_file_scrutiny_checklist_serializer import FileScrutinyCheckListSerializer

class FileScrutinyCheckListListCreateView(generics.ListCreateAPIView):
    queryset = FileScrutinyCheckList.objects.all()
    serializer_class = FileScrutinyCheckListSerializer

class FileScrutinyCheckListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileScrutinyCheckList.objects.all()
    serializer_class = FileScrutinyCheckListSerializer
