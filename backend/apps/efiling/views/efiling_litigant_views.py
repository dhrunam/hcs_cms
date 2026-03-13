from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingLitigant
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer


class EfilingLitigantListCreateView(ListCreateAPIView):
    queryset = EfilingLitigant.objects.all()
    serializer_class = EfilingLitigantSerializer


class EfilingLitigantRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingLitigant.objects.all()
    serializer_class = EfilingLitigantSerializer
