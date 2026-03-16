from rest_framework.generics import ListAPIView, ListCreateAPIView

from apps.core.models import CaseTypeT
from apps.master.serializers.case_type_t_serializers import CaseTypeTSerializer


class CaseTypeTListView(ListCreateAPIView):
    queryset = CaseTypeT.objects.all()
    serializer_class = CaseTypeTSerializer
