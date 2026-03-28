from rest_framework.generics import ListAPIView

from apps.efiling.models import EfilingNotification
from apps.efiling.serializers.notification_serializers import EfilingNotificationSerializer


class EfilingNotificationListView(ListAPIView):
    serializer_class = EfilingNotificationSerializer
    pagination_class = None

    def get_queryset(self):
        role = self.request.query_params.get("role")
        qs = EfilingNotification.objects.all().select_related("e_filing", "ia").order_by("-created_at")
        if role in ("advocate", "scrutiny_officer"):
            qs = qs.filter(role=role)
        return qs[:50]  # Last 50 notifications
