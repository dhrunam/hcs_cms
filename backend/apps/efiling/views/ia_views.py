from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import IA
from apps.efiling.serializers.ia_serializers import IASerializer


class IAListCreateView(ListCreateAPIView):
    queryset = IA.objects.all()
    serializer_class = IASerializer

    def get_queryset(self):
        qs = IA.objects.all().order_by("-id")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        e_filing = self.request.query_params.get("e_filing")
        if e_filing is not None:
            qs = qs.filter(e_filing=e_filing)
        return qs


class IARetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = IA.objects.all()
    serializer_class = IASerializer

    def get_queryset(self):
        qs = IA.objects.all().order_by("-id")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs
