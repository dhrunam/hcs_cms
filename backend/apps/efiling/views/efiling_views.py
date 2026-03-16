from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import Efiling
from apps.efiling.serializers.efiling_serializers import EfilingSerializer
 


class EfilingListCreateView(ListCreateAPIView):
    queryset = Efiling.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingSerializer
    


class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Efiling.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingSerializer
