"""Create dashboard notifications when key actions occur."""
from apps.efiling.models import EfilingNotification


def create_notification(role, notification_type, message, e_filing=None, ia=None, link_url=""):
    try:
        EfilingNotification.objects.create(
            role=role,
            notification_type=notification_type,
            message=message,
            e_filing=e_filing,
            ia=ia,
            link_url=link_url,
        )
    except Exception:
        pass  # Don't fail the main operation if notification creation fails
