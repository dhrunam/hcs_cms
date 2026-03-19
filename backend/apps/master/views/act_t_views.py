from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView

from apps.core.models import ActT
from apps.master.serializers.act_t_serializers import ActTSerializer


class ActTListView(ListCreateAPIView):
    queryset = ActT.objects.all()
    serializer_class = ActTSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
