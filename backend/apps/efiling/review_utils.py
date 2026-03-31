from django.utils import timezone
from django.db import models
from rest_framework.exceptions import ValidationError

from apps.core.models import Efiling, EfilingDocuments, EfilingDocumentsIndex, EfilingDocumentsScrutinyHistory
from apps.efiling.notification_utils import create_notification


def create_scrutiny_history(document_index, comments=None, user=None, scrutiny_status=None):
    history = EfilingDocumentsScrutinyHistory.objects.create(
        efiling_document_index=document_index,
        is_compliant=document_index.is_compliant,
        comments=comments if comments is not None else document_index.comments,
        scrutiny_status=scrutiny_status or document_index.scrutiny_status,
        recieved_at=timezone.now(),
        created_by=user,
        updated_by=user,
    )
    return history


def sync_document_index_for_upload(document, user=None, document_index_id=None):
    filing = document.e_filing
    status = (
        EfilingDocumentsIndex.ScrutinyStatus.DRAFT
        if filing.is_draft
        else EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
    )
    is_new_for_scrutiny = not filing.is_draft
    now = timezone.now()
    document_indexes = EfilingDocumentsIndex.objects.filter(document=document, is_active=True).order_by("id")

    if document_index_id is not None:
        document_indexes = document_indexes.filter(id=document_index_id)

    document_index = document_indexes.first()

    if document_index is None:
        last_sequence = (
            EfilingDocumentsIndex.objects.filter(document__e_filing=filing)
            .exclude(document_sequence__isnull=True)
            .order_by("-document_sequence")
            .values_list("document_sequence", flat=True)
            .first()
        )
        next_sequence = (last_sequence or 0) + 1
        document_index = EfilingDocumentsIndex.objects.create(
            document=document,
            document_part_name=document.document_type or "Uploaded document",
            file_part_path=document.final_document.name,
            document_sequence=next_sequence,
            comments=None,
            scrutiny_status=status,
            draft_scrutiny_status=None,
            draft_comments=None,
            draft_reviewed_at=None,
            is_new_for_scrutiny=is_new_for_scrutiny,
            last_resubmitted_at=now if is_new_for_scrutiny else None,
            created_by=user,
            updated_by=user,
        )
        create_scrutiny_history(
            document_index,
            comments="Document uploaded by advocate.",
            user=user,
            scrutiny_status=status,
        )
        if is_new_for_scrutiny and filing:
            create_notification(
                role="scrutiny_officer",
                notification_type="documents_uploaded",
                message=f"New documents uploaded for e-filing {filing.e_filing_number or filing.id}.",
                e_filing=filing,
                link_url=f"/scrutiny-officers/dashboard/filed-cases/details/{filing.id}",
            )
        return document_index

    for document_index in document_indexes:
        document_index.document_part_name = document.document_type or document_index.document_part_name
        document_index.file_part_path = document.final_document.name
        document_index.scrutiny_status = status
        document_index.draft_scrutiny_status = None
        document_index.draft_comments = None
        document_index.draft_reviewed_at = None
        document_index.is_compliant = False
        document_index.is_new_for_scrutiny = is_new_for_scrutiny
        document_index.last_resubmitted_at = now if is_new_for_scrutiny else document_index.last_resubmitted_at
        document_index.updated_by = user
        document_index.save(
            update_fields=[
                "document_part_name",
                "file_part_path",
                "scrutiny_status",
                "draft_scrutiny_status",
                "draft_comments",
                "draft_reviewed_at",
                "is_compliant",
                "is_new_for_scrutiny",
                "last_resubmitted_at",
                "updated_by",
                "updated_at",
            ]
        )
        create_scrutiny_history(
            document_index,
            comments="Document re-uploaded by advocate.",
            user=user,
            scrutiny_status=status,
        )
    if is_new_for_scrutiny and filing:
        create_notification(
            role="scrutiny_officer",
            notification_type="documents_uploaded",
            message=f"New documents uploaded for e-filing {filing.e_filing_number or filing.id}.",
            e_filing=filing,
            link_url=f"/scrutiny-officers/dashboard/filed-cases/details/{filing.id}",
        )
    return document_index if document_indexes else None


def submit_documents_for_scrutiny(filing, user=None):
    ensure_document_indexes_for_filing(filing, user=user)
    now = timezone.now()
    document_indexes = EfilingDocumentsIndex.objects.filter(document__e_filing=filing)

    for document_index in document_indexes:
        if document_index.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED:
            continue
        document_index.scrutiny_status = EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
        document_index.draft_scrutiny_status = None
        document_index.draft_comments = None
        document_index.draft_reviewed_at = None
        document_index.is_compliant = False
        document_index.is_new_for_scrutiny = True
        document_index.last_resubmitted_at = now
        document_index.updated_by = user
        document_index.save(
            update_fields=[
                "scrutiny_status",
                "draft_scrutiny_status",
                "draft_comments",
                "draft_reviewed_at",
                "is_compliant",
                "is_new_for_scrutiny",
                "last_resubmitted_at",
                "updated_by",
                "updated_at",
            ]
        )
        create_scrutiny_history(
            document_index,
            comments="Document sent to scrutiny queue.",
            user=user,
            scrutiny_status=document_index.scrutiny_status,
        )

    derive_filing_status(filing)
    create_notification(
        role="scrutiny_officer",
        notification_type="filing_submitted",
        message=f"New filing submitted for scrutiny: {filing.e_filing_number or filing.id}.",
        e_filing=filing,
        link_url=f"/scrutiny-officers/dashboard/filed-cases/details/{filing.id}",
    )


def ensure_document_indexes_for_filing(filing, user=None):
    documents = EfilingDocuments.objects.filter(e_filing=filing).order_by("id")

    for document in documents:
        if not document.final_document:
            continue
        existing_index = EfilingDocumentsIndex.objects.filter(document=document).order_by("id").first()
        if existing_index is None:
            sync_document_index_for_upload(document, user=user)


def derive_filing_status(filing):
    document_indexes = EfilingDocumentsIndex.objects.filter(
        document__e_filing=filing,
        is_active=True,
    )
    if not document_indexes.exists():
        # Backward-compatible fallback for rows that were accidentally stored inactive.
        document_indexes = EfilingDocumentsIndex.objects.filter(document__e_filing=filing)

    if filing.is_draft:
        filing.status = "DRAFT"
        filing.accepted_at = None
    elif not document_indexes.exists():
        filing.status = "UNDER_SCRUTINY"
        filing.accepted_at = None
    else:
        statuses = set(document_indexes.values_list("scrutiny_status", flat=True))
        if EfilingDocumentsIndex.ScrutinyStatus.REJECTED in statuses:
            if statuses == {EfilingDocumentsIndex.ScrutinyStatus.REJECTED}:
                filing.status = "REJECTED"
            else:
                filing.status = "PARTIALLY_REJECTED"
            filing.accepted_at = None
        elif statuses == {EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED}:
            # Only set ACCEPTED when case is registered. Until scrutiny officer
            # clicks "Register Case", keep UNDER_SCRUTINY so case status does not
            # change to Accepted when accepting replacement documents.
            if filing.case_number:
                filing.status = "ACCEPTED"
                latest_review_time = (
                    document_indexes.exclude(last_reviewed_at__isnull=True)
                    .order_by("-last_reviewed_at")
                    .values_list("last_reviewed_at", flat=True)
                    .first()
                )
                filing.accepted_at = latest_review_time or timezone.now()
            else:
                filing.status = "UNDER_SCRUTINY"
                filing.accepted_at = None
        else:
            filing.status = "UNDER_SCRUTINY"
            filing.accepted_at = None

    filing.save(update_fields=["status", "accepted_at", "updated_at"])
    return filing


def finalize_approved_filing(filing, user=None, bench=None):
    filing = derive_filing_status(filing)
    active_document_indexes = EfilingDocumentsIndex.objects.filter(
        document__e_filing=filing,
        is_active=True,
    )
    if not active_document_indexes.exists():
        active_document_indexes = EfilingDocumentsIndex.objects.filter(document__e_filing=filing)

    if filing.is_draft:
        raise ValidationError("Draft filings cannot be submitted as approved cases.")

    if not active_document_indexes.exists():
        raise ValidationError("At least one active document is required before submitting the case.")

    if active_document_indexes.exclude(
        scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED
    ).exists():
        raise ValidationError("All active documents must be approved before submitting the case.")

    if filing.case_number:
        if bench:
            filing.bench = bench
            filing.updated_by = user
            filing.save(update_fields=["bench", "updated_by", "updated_at"])
        return filing

    filing.case_number = filing.build_case_number()
    filing.status = "ACCEPTED"
    filing.bench = bench  # SET BENCH HERE
    latest_review_time = (
        active_document_indexes.exclude(last_reviewed_at__isnull=True)
        .order_by("-last_reviewed_at")
        .values_list("last_reviewed_at", flat=True)
        .first()
    )
    filing.accepted_at = latest_review_time or timezone.now()
    filing.updated_by = user
    filing.save(update_fields=["case_number", "status", "bench", "accepted_at", "updated_by", "updated_at"])
    return filing


def finalize_scrutiny_submission(filing, user=None, bench=None):
    if filing.is_draft:
        raise ValidationError("Draft filings cannot be submitted for scrutiny finalization.")

    document_indexes = EfilingDocumentsIndex.objects.filter(
        document__e_filing=filing,
        is_active=True,
    ).order_by("id")
    if not document_indexes.exists():
        document_indexes = EfilingDocumentsIndex.objects.filter(document__e_filing=filing).order_by("id")
    if not document_indexes.exists():
        raise ValidationError("At least one document is required before final submit.")

    now = timezone.now()
    final_statuses = []
    for document_index in document_indexes:
        final_status = document_index.draft_scrutiny_status or document_index.scrutiny_status
        if final_status not in (
            EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            EfilingDocumentsIndex.ScrutinyStatus.REJECTED,
        ):
            raise ValidationError("Please review all documents before final submit.")
        final_statuses.append(final_status)
        draft_comments = (
            document_index.draft_comments
            if document_index.draft_scrutiny_status is not None
            else document_index.comments
        )
        final_is_compliant = final_status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED
        reviewed_at = document_index.draft_reviewed_at or now
        document_index.scrutiny_status = final_status
        document_index.comments = draft_comments
        document_index.is_compliant = final_is_compliant
        document_index.is_new_for_scrutiny = False
        document_index.last_reviewed_at = reviewed_at
        document_index.draft_scrutiny_status = None
        document_index.draft_comments = None
        document_index.draft_reviewed_at = None
        document_index.updated_by = user
        document_index.save(
            update_fields=[
                "scrutiny_status",
                "comments",
                "is_compliant",
                "is_new_for_scrutiny",
                "last_reviewed_at",
                "draft_scrutiny_status",
                "draft_comments",
                "draft_reviewed_at",
                "updated_by",
                "updated_at",
            ]
        )
        create_scrutiny_history(
            document_index,
            comments=draft_comments,
            user=user,
            scrutiny_status=final_status,
        )

    has_rejected = EfilingDocumentsIndex.ScrutinyStatus.REJECTED in final_statuses
    if has_rejected:
        filing.status = (
            "PARTIALLY_REJECTED"
            if any(status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED for status in final_statuses)
            else "REJECTED"
        )
        filing.accepted_at = None
        if not filing.case_number:
            filing.case_number = None
        filing.updated_by = user
        filing.save(update_fields=["status", "accepted_at", "case_number", "updated_by", "updated_at"])
        create_notification(
            role="advocate",
            notification_type="scrutiny_partial" if filing.status == "PARTIALLY_REJECTED" else "scrutiny_rejected",
            message=f"E-filing {filing.e_filing_number or filing.id} has been {filing.status.replace('_', ' ').lower()}.",
            e_filing=filing,
            link_url=f"/advocate/dashboard/efiling/pending-scrutiny/details/{filing.id}",
        )
        return filing

    filing = finalize_approved_filing(filing, user=user, bench=bench)
    filing.refresh_from_db()
    create_notification(
        role="advocate",
        notification_type="scrutiny_accepted",
        message=f"E-filing {filing.e_filing_number or filing.id} has been accepted and registered.",
        e_filing=filing,
        link_url=f"/advocate/dashboard/efiling/pending-scrutiny/details/{filing.id}",
    )
    return filing


def can_replace_document(document, document_index_id=None):
    if document.e_filing.is_draft:
        return True

    document_indexes = (
        EfilingDocumentsIndex.objects.filter(document=document, is_active=True)
    )
    if document_index_id is not None:
        document_indexes = document_indexes.filter(id=document_index_id)

    return document_indexes.filter(
        models.Q(scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.REJECTED)
        | models.Q(draft_scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.REJECTED)
    ).exists()
