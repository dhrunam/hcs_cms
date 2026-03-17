from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingLitigant
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer


class EfilingLitigantListCreateView(ListCreateAPIView):
    queryset = EfilingLitigant.objects.all()
    serializer_class = EfilingLitigantSerializer

    def get_queryset(self):
        qs = EfilingLitigant.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

class EfilingLitigantRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingLitigant.objects.all()
    serializer_class = EfilingLitigantSerializer

    def get_queryset(self):
        qs = EfilingLitigant.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs   