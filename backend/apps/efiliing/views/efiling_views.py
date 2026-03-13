from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import Efiling
from apps.efiliing.serializers.efiling_serializers import EfilingSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
 


class EfilingListCreateView(ListCreateAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    


class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Efiling.objects.all()
    serializer_class = EfilingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
