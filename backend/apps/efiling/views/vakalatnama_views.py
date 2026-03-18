from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import Vakalatnama
from apps.efiling.serializers.vakalatnama_serializers import VakalatnamaSerializer


class VakalatnamaListCreateView(ListCreateAPIView):
    queryset = Vakalatnama.objects.all()
    serializer_class = VakalatnamaSerializer
    def get_queryset(self):
        qs = Vakalatnama.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs


class VakalatnamaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Vakalatnama.objects.all()
    serializer_class = VakalatnamaSerializer
    def get_queryset(self):
        qs = Vakalatnama.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs