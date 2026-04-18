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


class PaymentObjection(models.Model):
    """
    Tracks payment objections raised by scrutiny officer against an e-filing.
    When a scrutiny officer raises a payment objection, this record is created
    and the e-filing status is updated to reflect the objection.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RESOLVED = "RESOLVED", "Resolved"
        CANCELLED = "CANCELLED", "Cancelled"

    e_filing = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="payment_objections"
    )
    court_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The correct court fee amount as determined by the scrutiny officer"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Optional remarks explaining the payment objection"
    )
    raised_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="raised_payment_objections",
        help_text="The scrutiny officer who raised the objection"
    )
    raised_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the objection was resolved"
    )
    resolved_by_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The payment transaction ID that resolved this objection"
    )

    class Meta:
        db_table = "efiling_payment_objection"
        ordering = ["-raised_at"]
        verbose_name = "Payment Objection"
        verbose_name_plural = "Payment Objections"

    def __str__(self):
        return f"Payment Objection - {self.e_filing.e_filing_number} - ₹{self.court_fee_amount}"
