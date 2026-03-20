from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import IAActs
from apps.efiling.serializers.ia_acts_serializers import IAActsSerializer


class IAActsListCreateView(ListCreateAPIView):
    queryset = IAActs.objects.all()
    serializer_class = IAActsSerializer

    def get_queryset(self):
        qs = IAActs.objects.all().order_by("-id")
        is_active = self.request.query_params.get("is_active")
        ia_id = self.request.query_params.get("ia")
        efiling_id = self.request.query_params.get("e_filing")

        if ia_id is not None:
            qs = qs.filter(ia=ia_id)
        if efiling_id is not None:
            qs = qs.filter(e_filing=efiling_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs


class IAActsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = IAActs.objects.all()
    serializer_class = IAActsSerializer

    def get_queryset(self):
        qs = IAActs.objects.all().order_by("-id")
        is_active = self.request.query_params.get("is_active")
        ia_id = self.request.query_params.get("ia")
        efiling_id = self.request.query_params.get("e_filing")

        if ia_id is not None:
            qs = qs.filter(ia=ia_id)
        if efiling_id is not None:
            qs = qs.filter(e_filing=efiling_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs
