from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import EfilingActs
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer


class EfilingActsListCreateView(ListCreateAPIView):
    queryset = EfilingActs.objects.all()
    serializer_class = EfilingActsSerializer
    def get_queryset(self):
        qs = EfilingActs.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        efiling_id = self.request.query_params.get('efiling_id')
        if efiling_id is not None:
            qs = qs.filter(e_filing=efiling_id)
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs


class EfilingActsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingActs.objects.all()
    serializer_class = EfilingActsSerializer
    def get_queryset(self):
        qs = EfilingActs.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs