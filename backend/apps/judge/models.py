from __future__ import annotations

from django.db import models

from apps.accounts.models import User
from apps.core.models import BaseModel, Efiling
from apps.core.models import EfilingDocumentsIndex


JUDGE_GROUP_CJ = "JUDGE_CJ"
JUDGE_GROUP_J1 = "JUDGE_J1"
JUDGE_GROUP_J2 = "JUDGE_J2"


class CourtroomForward(BaseModel):
    """
    Listing Officer forwards an accepted case to judge(s) for a courtroom session.
    The case is tied to the forwarded_for_date and the bench_key at forwarding time.
    """

    forwarded_for_date = models.DateField()
    efiling = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name="courtroom_forwards")
    bench_key = models.CharField(max_length=50)
    forwarded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courtroom_forwards_created",
    )

    class Meta:
        db_table = "courtroom_forward"
        indexes = [models.Index(fields=["forwarded_for_date", "bench_key"])]


class CourtroomJudgeDecision(BaseModel):
    """
    Judge decision for a forwarded efiling + listing date.
    """

    judge_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courtroom_decisions"
    )
    efiling = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name="courtroom_decisions")
    forwarded_for_date = models.DateField()
    listing_date = models.DateField()
    approved = models.BooleanField(default=False)
    decision_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "courtroom_judge_decision"
        unique_together = ("judge_user", "efiling", "forwarded_for_date")
        indexes = [
            models.Index(fields=["listing_date", "approved"]),
            models.Index(fields=["forwarded_for_date", "approved"]),
        ]


class CourtroomDocumentAnnotation(BaseModel):
    """
    Judge annotations for a specific document index (shown when judge opens the doc).
    """

    judge_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courtroom_document_annotations"
    )
    efiling_document_index = models.ForeignKey(
        EfilingDocumentsIndex,
        on_delete=models.CASCADE,
        related_name="courtroom_annotations",
    )
    annotation_text = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "courtroom_document_annotation"
        unique_together = ("judge_user", "efiling_document_index")
        indexes = [models.Index(fields=["judge_user"])]

