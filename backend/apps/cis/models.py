from django.db import models


class CISFilingNumber(models.Model):
    """
    Represents a filing number issued by CIS 1.0 after scrutiny acceptance.
    This model tracks the EC-prefixed filing number linked to accepted e-filings.
    """

    case_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Case number (CIS filing number)",
        help_text="e.g., EC_SKNM01/2026/12345",
    )
    case_title = models.CharField(
        max_length=500,
        verbose_name="Case title from CIS",
    )
    case_type = models.CharField(
        max_length=50,
        verbose_name="Case type from CIS",
    )
    petitioner = models.CharField(
        max_length=300,
        verbose_name="Petitioner name from CIS",
    )
    respondent = models.CharField(
        max_length=300,
        verbose_name="Respondent name from CIS",
    )
    filing_date = models.DateField(
        verbose_name="Filing date in CIS",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created at",
    )

    class Meta:
        verbose_name = "CIS Filing Number"
        verbose_name_plural = "CIS Filing Numbers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.case_number} - {self.case_title}"


class CISDataLog(models.Model):
    """
    Audit log for all data transactions between CMS and CIS 1.0.
    Tracks successful and failed data consuming operations.
    """

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        PENDING = "PENDING", "Pending"

    operation = models.CharField(
        max_length=100,
        verbose_name="Operation type",
        help_text="e.g., FILING_NUMBER_GENERATION, DATA_SYNC",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status",
    )
    source_case_id = models.CharField(
        max_length=100,
        verbose_name="Source case ID (from CMS)",
    )
    target_case_number = models.CharField(
        max_length=100,
        verbose_name="Target case number (from CIS)",
        null=True,
        blank=True,
    )
    payload = models.JSONField(
        verbose_name="Payload sent",
        null=True,
        blank=True,
    )
    response = models.JSONField(
        verbose_name="Response received",
        null=True,
        blank=True,
    )
    error_message = models.TextField(
        verbose_name="Error message",
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp",
    )

    class Meta:
        verbose_name = "CIS Data Log"
        verbose_name_plural = "CIS Data Logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.operation} - {self.status} ({self.timestamp})"
