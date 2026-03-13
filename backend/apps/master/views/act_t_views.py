from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import ActT
from apps.master.serializers.act_t_serializers import ActTSerializer


class ActTListView(ListAPIView):
    queryset = ActT.objects.all()
    serializer_class = ActTSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
