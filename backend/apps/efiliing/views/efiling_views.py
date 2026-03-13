from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import Efiling
from apps.efiliing.serializers.efiling_serializers import EfilingSerializer


class EfilingListCreateView(ListCreateAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer


class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer
