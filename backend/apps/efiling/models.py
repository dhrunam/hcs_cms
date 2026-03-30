from django.db import models

from apps.core.models import Efiling, IA


class EfilingNotification(models.Model):
    """Notifications for dashboard - advocate or scrutiny officer."""

    class Role(models.TextChoices):
        ADVOCATE = "advocate", "Advocate"
        SCRUTINY_OFFICER = "scrutiny_officer", "Scrutiny Officer"

    class NotificationType(models.TextChoices):
        FILING_SUBMITTED = "filing_submitted", "Filing Submitted"
        DOCUMENTS_UPLOADED = "documents_uploaded", "Documents Uploaded"
        IA_FILED = "ia_filed", "IA Filed"
        SCRUTINY_ACCEPTED = "scrutiny_accepted", "Scrutiny Accepted"
        SCRUTINY_REJECTED = "scrutiny_rejected", "Scrutiny Rejected"
        SCRUTINY_PARTIAL = "scrutiny_partial", "Scrutiny Partially Rejected"

    role = models.CharField(max_length=32, choices=Role.choices, db_index=True)
    notification_type = models.CharField(max_length=64, choices=NotificationType.choices)
    message = models.CharField(max_length=500)
    e_filing = models.ForeignKey(
        Efiling, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    ia = models.ForeignKey(
        IA, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    link_url = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "efiling_notification"
        ordering = ["-created_at"]
