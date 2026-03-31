from __future__ import annotations

from django.db import models

from apps.accounts.models import User
from apps.core.models import BaseModel, Efiling
from apps.core.models import EfilingDocumentsIndex

class CourtroomForward(BaseModel):
    """
    Reader forwards an accepted case to judge(s) for a courtroom session.
    The case is tied to the forwarded_for_date and the bench_key at forwarding time.
    """

    forwarded_for_date = models.DateField()
    efiling = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name="courtroom_forwards")
    bench_key = models.CharField(max_length=50)
    listing_summary = models.TextField(blank=True, null=True)
    forwarded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courtroom_forwards_created",
    )

    class Meta:
        db_table = "courtroom_forward"
        app_label = "reader"
        indexes = [models.Index(fields=["forwarded_for_date", "bench_key"])]


class CourtroomForwardDocument(BaseModel):
    """
    Documents explicitly selected by Reader for a forwarded case request.
    """

    forward = models.ForeignKey(
        CourtroomForward,
        on_delete=models.CASCADE,
        related_name="selected_documents",
    )
    efiling_document_index = models.ForeignKey(
        EfilingDocumentsIndex,
        on_delete=models.CASCADE,
        related_name="forwarded_requests",
    )

    class Meta:
        db_table = "courtroom_forward_document"
        app_label = "reader"
        unique_together = ("forward", "efiling_document_index")
        indexes = [
            models.Index(fields=["forward"]),
            models.Index(fields=["efiling_document_index"]),
        ]
