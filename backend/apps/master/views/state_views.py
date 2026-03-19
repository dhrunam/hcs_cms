from rest_framework import permissions
from rest_framework.generics import ListAPIView

from apps.core.models import State
from apps.master.serializers.state_serializers import StateSerializer


class StateListView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
