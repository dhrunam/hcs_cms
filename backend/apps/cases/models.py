from django.conf import settings
from django.db import models


class Case(models.Model):
    """Represents a legal case managed by the HCS Case Management System."""

    class CaseType(models.TextChoices):
        CIVIL = "CIVIL", "Civil"
        CRIMINAL = "CRIMINAL", "Criminal"
        WRIT = "WRIT", "Writ"
        APPEAL = "APPEAL", "Appeal"
        MISC = "MISC", "Miscellaneous"

    class CaseStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ADMITTED = "ADMITTED", "Admitted"
        DISPOSED = "DISPOSED", "Disposed"
        TRANSFERRED = "TRANSFERRED", "Transferred"
        MISC = "MISC", "Miscellaneous"

    case_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Case number",
    )
    case_type = models.CharField(
        max_length=20,
        choices=CaseType.choices,
        default=CaseType.MISC,
        verbose_name="Case type",
    )
    case_title = models.CharField(
        max_length=500,
        verbose_name="Case title",
    )
    petitioner_name = models.CharField(
        max_length=300,
        verbose_name="Petitioner name",
    )
    respondent_name = models.CharField(
        max_length=300,
        verbose_name="Respondent name",
    )
    filed_date = models.DateField(verbose_name="Filed date")
    status = models.CharField(
        max_length=20,
        choices=CaseStatus.choices,
        default=CaseStatus.PENDING,
        verbose_name="Status",
        db_index=True,
    )
    bench = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Bench",
    )
    judge_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Judge name",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cases_created",
        verbose_name="Created by",
    )

    class Meta:
        verbose_name = "Case"
        verbose_name_plural = "Cases"
        ordering = ["-filed_date", "case_number"]
        indexes = [
            models.Index(fields=["case_type"], name="idx_case_type"),
            models.Index(fields=["status", "case_type"], name="idx_status_case_type"),
        ]

    def __str__(self) -> str:
        return f"{self.case_number} – {self.case_title}"
