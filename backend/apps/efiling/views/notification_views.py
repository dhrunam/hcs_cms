import logging

from django.db.models import Q
from django.db.utils import ProgrammingError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.efiling.models import EfilingNotification
from apps.efiling.serializers.notification_serializers import EfilingNotificationSerializer

logger = logging.getLogger(__name__)


class EfilingNotificationListView(ListAPIView):
    serializer_class = EfilingNotificationSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ProgrammingError as exc:
            if "efiling_notification" not in str(exc):
                raise
            logger.warning(
                "efiling_notification missing; run: python manage.py migrate efiling",
                exc_info=True,
            )
            return Response([])

    def get_queryset(self):
        role = self.request.query_params.get("role")
        qs = (
            EfilingNotification.objects.all()
            .select_related("e_filing", "ia", "ia__e_filing")
            .order_by("-created_at")
        )
        if role in ("advocate", "scrutiny_officer"):
            qs = qs.filter(role=role)

        if role == "advocate":
            user = self.request.user
            if not getattr(user, "is_authenticated", False):
                return qs.none()

            qs = qs.filter(
                Q(e_filing__created_by=user)
                | Q(ia__e_filing__created_by=user)
            )

        return qs[:50]  # Last 50 notifications
