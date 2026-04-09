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


class ReaderDailyProceeding(BaseModel):
    class ListingSyncStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SYNCED = "SYNCED", "Synced"
        FAILED = "FAILED", "Failed"

    efiling = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="reader_daily_proceedings",
    )
    bench_key = models.CharField(max_length=50)
    hearing_date = models.DateField()
    next_listing_date = models.DateField()
    proceedings_text = models.TextField()
    reader_remark = models.TextField(blank=True, null=True)
    listing_sync_status = models.CharField(
        max_length=20,
        choices=ListingSyncStatus.choices,
        default=ListingSyncStatus.PENDING,
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reader_daily_proceedings_submitted",
    )

    class Meta:
        db_table = "reader_daily_proceeding"
        app_label = "reader"
        constraints = [
            models.UniqueConstraint(
                fields=["efiling", "hearing_date", "bench_key"],
                name="reader_daily_proceeding_unique_case_hearing_bench",
            ),
        ]
        indexes = [
            models.Index(fields=["bench_key", "hearing_date"]),
            models.Index(fields=["next_listing_date"]),
        ]


class StenoOrderWorkflow(BaseModel):
    class DocumentType(models.TextChoices):
        ORDER = "ORDER", "Order"
        JUDGMENT = "JUDGMENT", "Judgment"

    class WorkflowStatus(models.TextChoices):
        PENDING_UPLOAD = "PENDING_UPLOAD", "Pending Upload"
        UPLOADED_BY_STENO = "UPLOADED_BY_STENO", "Uploaded by Steno"
        SENT_FOR_JUDGE_APPROVAL = "SENT_FOR_JUDGE_APPROVAL", "Sent for Judge Approval"
        CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"
        JUDGE_APPROVED = "JUDGE_APPROVED", "Judge Approved"
        SIGNED_AND_PUBLISHED = "SIGNED_AND_PUBLISHED", "Signed and Published"

    class JudgeApprovalStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    proceeding = models.ForeignKey(
        ReaderDailyProceeding,
        on_delete=models.CASCADE,
        related_name="steno_workflows",
    )
    efiling = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="steno_workflows",
    )
    assigned_steno = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_steno_workflows",
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.ORDER,
    )
    draft_document_index = models.ForeignKey(
        EfilingDocumentsIndex,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="steno_draft_workflows",
    )
    signed_document_index = models.ForeignKey(
        EfilingDocumentsIndex,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="steno_signed_workflows",
    )
    workflow_status = models.CharField(
        max_length=40,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.PENDING_UPLOAD,
    )
    judge_approval_status = models.CharField(
        max_length=20,
        choices=JudgeApprovalStatus.choices,
        default=JudgeApprovalStatus.PENDING,
    )
    judge_approval_notes = models.TextField(blank=True, null=True)
    judge_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="judge_approved_steno_workflows",
    )
    judge_approved_at = models.DateTimeField(blank=True, null=True)
    digitally_signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="steno_digitally_signed_workflows",
    )
    digitally_signed_at = models.DateTimeField(blank=True, null=True)
    digital_signature_provider = models.CharField(max_length=100, blank=True, null=True)
    digital_signature_certificate_serial = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    digital_signature_signer_name = models.CharField(max_length=200, blank=True, null=True)
    digital_signature_reason = models.TextField(blank=True, null=True)
    digital_signature_metadata = models.JSONField(blank=True, null=True, default=dict)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "steno_order_workflow"
        app_label = "reader"
        constraints = [
            models.UniqueConstraint(
                fields=["proceeding", "document_type"],
                name="steno_workflow_unique_proceeding_doc_type",
            ),
        ]
        indexes = [
            models.Index(fields=["assigned_steno", "workflow_status"]),
            models.Index(fields=["judge_approval_status"]),
        ]
