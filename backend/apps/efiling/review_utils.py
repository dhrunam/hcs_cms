from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.models import Efiling, EfilingDocuments, EfilingDocumentsIndex, EfilingDocumentsScrutinyHistory


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


def sync_document_index_for_upload(document, user=None):
    filing = document.e_filing
    status = (
        EfilingDocumentsIndex.ScrutinyStatus.DRAFT
        if filing.is_draft
        else EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
    )
    is_new_for_scrutiny = not filing.is_draft
    now = timezone.now()
    document_index = (
        EfilingDocumentsIndex.objects.filter(document=document).order_by("id").first()
    )

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
        return document_index

    document_index.document_part_name = document.document_type or document_index.document_part_name
    document_index.file_part_path = document.final_document.name
    document_index.scrutiny_status = status
    document_index.is_compliant = False
    document_index.is_new_for_scrutiny = is_new_for_scrutiny
    document_index.last_resubmitted_at = now if is_new_for_scrutiny else document_index.last_resubmitted_at
    document_index.updated_by = user
    document_index.save(
        update_fields=[
            "document_part_name",
            "file_part_path",
            "scrutiny_status",
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
    return document_index


def submit_documents_for_scrutiny(filing, user=None):
    ensure_document_indexes_for_filing(filing, user=user)
    now = timezone.now()
    document_indexes = EfilingDocumentsIndex.objects.filter(document__e_filing=filing)

    for document_index in document_indexes:
        if document_index.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED:
            continue
        document_index.scrutiny_status = EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
        document_index.is_compliant = False
        document_index.is_new_for_scrutiny = True
        document_index.last_resubmitted_at = now
        document_index.updated_by = user
        document_index.save(
            update_fields=[
                "scrutiny_status",
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

    if filing.is_draft:
        filing.status = "DRAFT"
        filing.accepted_at = None
    elif not document_indexes.exists():
        filing.status = "UNDER_SCRUTINY"
        filing.accepted_at = None
    else:
        statuses = set(document_indexes.values_list("scrutiny_status", flat=True))
        if EfilingDocumentsIndex.ScrutinyStatus.REJECTED in statuses:
            filing.status = "REJECTED"
            filing.accepted_at = None
        elif statuses == {EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED}:
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

    filing.save(update_fields=["status", "accepted_at", "updated_at"])
    return filing


def finalize_approved_filing(filing, user=None):
    filing = derive_filing_status(filing)
    active_document_indexes = EfilingDocumentsIndex.objects.filter(
        document__e_filing=filing,
        is_active=True,
    )

    if filing.is_draft:
        raise ValidationError("Draft filings cannot be submitted as approved cases.")

    if not active_document_indexes.exists():
        raise ValidationError("At least one active document is required before submitting the case.")

    if active_document_indexes.exclude(
        scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED
    ).exists():
        raise ValidationError("All active documents must be approved before submitting the case.")

    if filing.case_number:
        return filing

    filing.case_number = filing.build_case_number()
    filing.updated_by = user
    filing.save(update_fields=["case_number", "updated_by", "updated_at"])
    return filing


def can_replace_document(document):
    if document.e_filing.is_draft:
        return True

    document_index = (
        EfilingDocumentsIndex.objects.filter(document=document, is_active=True)
        .order_by("id")
        .first()
    )
    return (
        document_index is not None
        and document_index.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.REJECTED
    )
