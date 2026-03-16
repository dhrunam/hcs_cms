from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingActs
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer


class EfilingActsListCreateView(ListCreateAPIView):
    queryset = EfilingActs.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingActsSerializer


class EfilingActsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingActs.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingActsSerializer
