from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import CaseTypeT
from apps.master.serializers.case_type_t_serializers import CaseTypeTSerializer


class CaseTypeTListView(ListCreateAPIView):
    queryset = CaseTypeT.objects.all().order_by('type_name')
    serializer_class = CaseTypeTSerializer
    pagination_class = None  # Disable pagination for this view
    permission_classes = [IsAuthenticatedOrReadOnly]
