from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import State
from apps.master.serializers.state_serializers import StateSerializer


class StateListView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
