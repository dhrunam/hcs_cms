from django.db import models

from apps.accounts.models import User
from apps.core.models import BaseModel, Efiling


class OfficeNote(BaseModel):
    efiling = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="office_notes",
    )
    note_content = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_office_notes",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_office_notes",
    )

    class Meta:
        db_table = "office_note"
        app_label = "office_notes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["efiling", "-created_at"]),
        ]

    def __str__(self):
        return f"OfficeNote {self.id} - Case {self.efiling_id}"