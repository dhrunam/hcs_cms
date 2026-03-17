from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import IA
from apps.efiling.serializers.ia_serializers import IASerializer


class IAListCreateView(ListCreateAPIView):
    """List and create IA records (metadata only)."""

    serializer_class = IASerializer

    def get_queryset(self):
        qs = IA.objects.all().order_by("-id")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs


class IARetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single IA record."""

    serializer_class = IASerializer

    def get_queryset(self):
        qs = IA.objects.all().order_by("-id")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs
        
