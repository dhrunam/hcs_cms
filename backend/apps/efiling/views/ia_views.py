from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.core.models import IA
from apps.efiling.notification_utils import create_notification
from apps.efiling.ia_court_fee import normalize_ia_status
from apps.efiling.serializers.ia_serializers import IASerializer


class IAListCreateView(ListCreateAPIView):
    queryset = IA.objects.all()
    serializer_class = IASerializer

    def get_queryset(self):
        qs = (
            IA.objects.all()
            .order_by("-id")
            .select_related("e_filing")
            .prefetch_related("e_filing__litigants")
        )
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        e_filing = self.request.query_params.get("e_filing")
        if e_filing is not None:
            qs = qs.filter(e_filing=e_filing)
        return qs

    def perform_create(self, serializer):
        ia = serializer.save()
        if ia.e_filing_id and normalize_ia_status(ia.status) == "UNDER_SCRUTINY":
            create_notification(
                role="scrutiny_officer",
                notification_type="ia_filed",
                message=f"New IA filed: {ia.ia_number or ia.id} for e-filing {ia.e_filing.e_filing_number or ia.e_filing_id}.",
                e_filing=ia.e_filing,
                ia=ia,
                link_url=f"/scrutiny-officers/dashboard/filed-cases/details/{ia.e_filing_id}",
            )


class IARetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = IA.objects.all()
    serializer_class = IASerializer

    def get_queryset(self):
        qs = (
            IA.objects.all()
            .order_by("-id")
            .select_related("e_filing")
            .prefetch_related("e_filing__litigants")
        )
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs

    def perform_update(self, serializer):
        prev_status = normalize_ia_status(serializer.instance.status)
        ia = serializer.save()
        new_status = normalize_ia_status(ia.status)
        if (
            new_status == "UNDER_SCRUTINY"
            and prev_status != "UNDER_SCRUTINY"
            and ia.e_filing_id
        ):
            create_notification(
                role="scrutiny_officer",
                notification_type="ia_filed",
                message=f"New IA filed: {ia.ia_number or ia.id} for e-filing {ia.e_filing.e_filing_number or ia.e_filing_id}.",
                e_filing=ia.e_filing,
                ia=ia,
                link_url=f"/scrutiny-officers/dashboard/filed-cases/details/{ia.e_filing_id}",
            )
