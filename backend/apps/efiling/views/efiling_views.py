from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import Efiling
from apps.efiling.serializers.efiling_serializers import EfilingSerializer

 
class EfilingListCreateView(ListCreateAPIView):
    serializer_class = EfilingSerializer
    def get_queryset(self):
        qs = Efiling.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

    

class EfilingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = EfilingSerializer
    def get_queryset(self):
        qs = Efiling.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs


