from rest_framework import generics
from apps.core.models import FileScrutinyCheckList
from apps.efiling.serializers.efiling_file_scrutiny_checklist_serializer import FileScrutinyCheckListSerializer

class FileScrutinyCheckListListCreateView(generics.ListCreateAPIView):
    queryset = FileScrutinyCheckList.objects.all()
    serializer_class = FileScrutinyCheckListSerializer

    def get_queryset(self):
        qs = FileScrutinyCheckList.objects.all().order_by("id")
        case_type = self.request.query_params.get("case_type")
        if case_type is not None:
            qs = qs.filter(case_type=case_type)
        return qs

class FileScrutinyCheckListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileScrutinyCheckList.objects.all()
    serializer_class = FileScrutinyCheckListSerializer
