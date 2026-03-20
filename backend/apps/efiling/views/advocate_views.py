from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.core.models import AdvocateT
from apps.efiling.serializers.advocate_serializers import AdvocateSerializer


class AdvocateListView(ListAPIView):
    serializer_class = AdvocateSerializer
    queryset = AdvocateT.objects.all()

    def get_queryset(self):
        queryset = self.queryset.order_by("-adv_code")

        search = self.request.query_params.get("search")
        adv_code = self.request.query_params.get("adv_code")
        is_active = self.request.query_params.get("is_active")

        if search:
            queryset = queryset.filter(
                Q(adv_name__icontains=search)
                | Q(adv_full_name__icontains=search)
                | Q(adv_reg__icontains=search)
            )

        if adv_code:
            queryset = queryset.filter(adv_code=adv_code)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ["true", "1"])

        return queryset


class AdvocateRetrieveView(RetrieveAPIView):
    queryset = AdvocateT.objects.all()
    serializer_class = AdvocateSerializer
    lookup_field = "adv_code"
