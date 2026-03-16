from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingLitigant
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer


class EfilingLitigantListCreateView(ListCreateAPIView):
    queryset = EfilingLitigant.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingLitigantSerializer


class EfilingLitigantRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingLitigant.objects.filter(is_active=True).order_by('-id')
    serializer_class = EfilingLitigantSerializer
