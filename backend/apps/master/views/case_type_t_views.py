from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import CaseTypeT
from apps.master.serializers.case_type_t_serializers import CaseTypeTSerializer


class CaseTypeTListView(ListAPIView):
    queryset = CaseTypeT.objects.all()
    serializer_class = CaseTypeTSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
