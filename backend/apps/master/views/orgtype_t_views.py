from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import OrgtypeT
from apps.master.serializers.orgtype_t_serializers import OrgtypeTSerializer


class OrgtypeTListView(ListAPIView):
    queryset = OrgtypeT.objects.all()
    serializer_class = OrgtypeTSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
