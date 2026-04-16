from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import PurposeT
from apps.master.serializers.purpose_t_serializers import PurposeTSerializer


class PurposeTListView(ListCreateAPIView):
    queryset = PurposeT.objects.filter(is_active=True).order_by("purpose_priority", "purpose_name", "purpose_code")
    serializer_class = PurposeTSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]