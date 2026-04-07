from __future__ import annotations

from django.db import models

from apps.accounts.models import User
from apps.core.models import BaseModel, Efiling
from apps.core.models import EfilingDocumentsIndex


JUDGE_GROUP_CJ = "API_JUDGE"
JUDGE_GROUP_J1 = "API_JUDGE"
JUDGE_GROUP_J2 = "API_JUDGE"



class CourtroomJudgeDecision(BaseModel):
    """
    Judge decision for a forwarded efiling + listing date.
    """

    class DecisionStatus(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        DECLINED = "DECLINED", "Declined"
        REQUESTED_DOCS = "REQUESTED_DOCS", "Requested Documents"

    judge_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courtroom_decisions"
    )
    efiling = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name="courtroom_decisions")
    forwarded_for_date = models.DateField()
    listing_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=DecisionStatus.choices,
        default=DecisionStatus.DECLINED,
    )
    approved = models.BooleanField(default=False)
    decision_notes = models.TextField(blank=True, null=True)
    reader_listing_remark = models.TextField(blank=True, null=True)
    # Canonical role this row satisfies for reader approval flows (JUDGE_CJ, JUDGE_J1, …).
    # Decouples from judge_user__groups when SSO only exposes API_JUDGE.
    bench_role_group = models.CharField(max_length=32, blank=True, null=True, db_index=True)

    class Meta:
        db_table = "courtroom_judge_decision"
        unique_together = ("judge_user", "efiling", "forwarded_for_date")
        indexes = [
            models.Index(fields=["listing_date", "approved"]),
            models.Index(fields=["forwarded_for_date", "approved"]),
        ]



class CourtroomDecisionRequestedDocument(BaseModel):
    """
    Document list explicitly requested by judge for a decision row.
    """

    judge_decision = models.ForeignKey(
        CourtroomJudgeDecision,
        on_delete=models.CASCADE,
        related_name="requested_documents",
    )
    efiling_document_index = models.ForeignKey(
        EfilingDocumentsIndex,
        on_delete=models.CASCADE,
        related_name="judge_requested_documents",
    )

    class Meta:
        db_table = "courtroom_decision_requested_document"
        unique_together = ("judge_decision", "efiling_document_index")
        indexes = [
            models.Index(fields=["judge_decision"]),
            models.Index(fields=["efiling_document_index"]),
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
    annotation_data = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        db_table = "courtroom_document_annotation"
        unique_together = ("judge_user", "efiling_document_index")
        indexes = [models.Index(fields=["judge_user"])]


class CourtroomSharedView(BaseModel):
    """
    Advocate sharing their current document + page index with judges.
    """
    efiling = models.ForeignKey(
        Efiling, on_delete=models.CASCADE, related_name="shared_views"
    )
    advocate_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shared_views"
    )
    document_index_id = models.IntegerField()
    page_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "courtroom_shared_view"
        unique_together = ("efiling", "advocate_user")
        indexes = [models.Index(fields=["efiling", "is_active"])]
