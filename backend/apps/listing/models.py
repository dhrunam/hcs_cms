from __future__ import annotations

from django.db import models

from apps.core.models import Efiling
from apps.core.models import BaseModel
from apps.accounts.models import User


class CauseList(BaseModel):
    class CauseListStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"

    cause_list_date = models.DateField()
    # bench_key is a string representation of the bench/division bench combination
    # (e.g. "CJ", "Judge1", "CJ+Judge1", etc.)
    bench_key = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=CauseListStatus.choices,
        default=CauseListStatus.DRAFT,
    )

    # Explicit field to match workflow semantics; BaseModel also has created_by/updated_by.
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cause_lists_generated",
    )

    published_at = models.DateTimeField(blank=True, null=True)
    pdf_file = models.FileField(
        upload_to="causelists/",
        blank=True,
        null=True,
        max_length=512,
    )

    class Meta:
        db_table = "cause_list"
        unique_together = ("cause_list_date", "bench_key")
        indexes = [
            models.Index(fields=["cause_list_date", "status"]),
        ]

    def __str__(self) -> str:
        return f"CauseList({self.cause_list_date}, {self.bench_key}, {self.status})"


class CauseListEntry(BaseModel):
    cause_list = models.ForeignKey(
        CauseList,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    efiling = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="cause_list_entries",
    )

    # Manual ordering as set by Listing Officer.
    serial_no = models.PositiveIntegerField(blank=True, null=True)
    included = models.BooleanField(default=True)

    petitioner_advocate = models.TextField(blank=True, null=True)
    respondent_advocate = models.TextField(blank=True, null=True)

    selected_ias = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "cause_list_entry"
        unique_together = ("cause_list", "efiling")
        indexes = [
            models.Index(fields=["cause_list", "included"]),
        ]

    def __str__(self) -> str:
        return f"CauseListEntry({self.cause_list_id}, {self.efiling_id}, {self.included})"

