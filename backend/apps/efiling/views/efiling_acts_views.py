from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import EfilingActs
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer


class EfilingActsListCreateView(ListCreateAPIView):
    queryset = EfilingActs.objects.all()
    serializer_class = EfilingActsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EfilingActsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingActs.objects.all()
    serializer_class = EfilingActsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
