from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from apps.core.models import Efiling, EfilingDocumentsIndex
from apps.efiling.pdf_validators import validate_pdf_file
from apps.efiling.review_utils import (
    can_replace_document,
    create_scrutiny_history,
    derive_filing_status,
    ensure_document_indexes_for_filing,
)
from apps.efiling.serializers.efiling_document_index import EfilingDocumentsIndexSerializer


class EfilingDocumentsIndexListCreateView(ListCreateAPIView):
    serializer_class = EfilingDocumentsIndexSerializer

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        efiling_id = self.request.query_params.get("efiling_id")
        document_id = self.request.query_params.get("document_id")
        scrutiny_status = self.request.query_params.get("scrutiny_status")
        is_new_for_scrutiny = self.request.query_params.get("is_new_for_scrutiny")
        is_ia = self.request.query_params.get("is_ia")

        if efiling_id is not None:
            filing = Efiling.objects.filter(pk=efiling_id).first()
            if filing is not None:
                ensure_document_indexes_for_filing(filing)

        qs = EfilingDocumentsIndex.objects.select_related("document", "document__e_filing").all()
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        if efiling_id is not None:
            qs = qs.filter(document__e_filing=efiling_id)
        if is_ia is not None:
            qs = qs.filter(document__is_ia=is_ia.lower() in ["true", "1"])
        if document_id is not None:
            qs = qs.filter(document=document_id)
        if scrutiny_status is not None:
            qs = qs.filter(scrutiny_status=scrutiny_status)
        if is_new_for_scrutiny is not None:
            qs = qs.filter(is_new_for_scrutiny=is_new_for_scrutiny.lower() in ["true", "1"])
        if efiling_id is not None:
            return qs.order_by("document_sequence", "id")
        return qs.order_by("-id")

    def perform_create(self, serializer):
        with transaction.atomic():
            now = timezone.now()
            filing = serializer.validated_data.get("document").e_filing if serializer.validated_data.get("document") else None
            is_draft_filing = bool(filing and filing.is_draft)
            scrutiny_status = (
                EfilingDocumentsIndex.ScrutinyStatus.DRAFT
                if is_draft_filing
                else EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
            )
            instance = serializer.save(
                is_active=True,
                scrutiny_status=scrutiny_status,
                draft_scrutiny_status=None,
                draft_comments=None,
                draft_reviewed_at=None,
                is_compliant=False,
                is_new_for_scrutiny=bool(filing and not filing.is_draft),
                last_resubmitted_at=now if filing and not filing.is_draft else None,
                created_by=self.request.user if self.request.user.is_authenticated else None,
                updated_by=self.request.user if self.request.user.is_authenticated else None,
            )
            create_scrutiny_history(
                instance,
                comments=instance.comments or "Document review item created.",
                user=self.request.user if self.request.user.is_authenticated else None,
                scrutiny_status=instance.scrutiny_status,
            )
            if instance.document and instance.document.e_filing:
                derive_filing_status(instance.document.e_filing)


class EfilingDocumentsIndexRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = EfilingDocumentsIndexSerializer

    def get_queryset(self):
        qs = (
            EfilingDocumentsIndex.objects.select_related("document", "document__e_filing")
            .all()
            .order_by("-id")
        )
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        return qs

    def update(self, request, *args, **kwargs):
        return self._save_review_update(request, *args, partial=False, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._save_review_update(request, *args, partial=True, **kwargs)

    def _save_review_update(self, request, *args, partial=False, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            is_file_replacement = "file_part_path" in request.FILES or "file_part_path" in request.data

            if is_file_replacement and not can_replace_document(instance.document, document_index_id=instance.id):
                raise ValidationError(
                    {
                        "file_part_path": (
                            "This document can only be replaced after the scrutiny officer rejects it."
                        )
                    }
                )

            if is_file_replacement:
                uploaded_file = request.FILES.get("file_part_path") or request.data.get("file_part_path")
                if not uploaded_file:
                    raise ValidationError({"file_part_path": "A PDF file is required."})
                validate_pdf_file(uploaded_file, "file_part_path")

                instance.file_part_path = uploaded_file
                instance.is_active = True
                filing = instance.document.e_filing if instance.document else None
                scrutiny_status = (
                    EfilingDocumentsIndex.ScrutinyStatus.DRAFT
                    if filing and filing.is_draft
                    else EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
                )
                instance.scrutiny_status = scrutiny_status
                instance.draft_scrutiny_status = None
                instance.draft_comments = None
                instance.draft_reviewed_at = None
                instance.is_compliant = False
                instance.is_new_for_scrutiny = bool(filing and not filing.is_draft)
                instance.last_resubmitted_at = timezone.now() if instance.is_new_for_scrutiny else None
                instance.updated_by = request.user if request.user.is_authenticated else None
                instance.save(
                    update_fields=[
                        "file_part_path",
                        "is_active",
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
                    instance,
                    comments="Document re-uploaded by advocate.",
                    user=request.user if request.user.is_authenticated else None,
                    scrutiny_status=instance.scrutiny_status,
                )
                if filing:
                    derive_filing_status(filing)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)

            if "scrutiny_status" in request.data or "comments" in request.data:
                review_status = request.data.get("scrutiny_status", instance.draft_scrutiny_status)
                if review_status not in (
                    EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
                    EfilingDocumentsIndex.ScrutinyStatus.REJECTED,
                ):
                    raise ValidationError(
                        {"scrutiny_status": "Review status must be ACCEPTED or REJECTED."}
                    )
                review_comments = request.data.get("comments", instance.draft_comments)
                filing = instance.document.e_filing if instance.document else None
                case_already_accepted = bool(filing and filing.case_number)

                if case_already_accepted:
                    instance.scrutiny_status = review_status
                    instance.comments = review_comments
                    instance.is_compliant = review_status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED
                    instance.draft_scrutiny_status = None
                    instance.draft_comments = None
                    instance.draft_reviewed_at = None
                    instance.last_reviewed_at = timezone.now()
                    # Keep this review item in the active scrutiny cycle until
                    # scrutiny officer submits the new review batch.
                    instance.is_new_for_scrutiny = True
                    instance.updated_by = request.user if request.user.is_authenticated else None
                    instance.save(
                        update_fields=[
                            "scrutiny_status",
                            "comments",
                            "is_compliant",
                            "draft_scrutiny_status",
                            "draft_comments",
                            "draft_reviewed_at",
                            "last_reviewed_at",
                            "is_new_for_scrutiny",
                            "updated_by",
                            "updated_at",
                        ]
                    )
                    create_scrutiny_history(
                        instance,
                        comments=review_comments,
                        user=request.user if request.user.is_authenticated else None,
                        scrutiny_status=review_status,
                    )
                    if filing:
                        derive_filing_status(filing)
                else:
                    instance.draft_scrutiny_status = review_status
                    instance.draft_comments = review_comments
                    instance.draft_reviewed_at = timezone.now()
                    instance.is_active = True
                    instance.is_new_for_scrutiny = False
                    instance.updated_by = request.user if request.user.is_authenticated else None
                    instance.save(
                        update_fields=[
                            "is_active",
                            "draft_scrutiny_status",
                            "draft_comments",
                            "draft_reviewed_at",
                            "is_new_for_scrutiny",
                            "updated_by",
                            "updated_at",
                        ]
                    )
                serializer = self.get_serializer(instance)
                return Response(serializer.data)

            kwargs["partial"] = partial
            return super().update(request, *args, **kwargs)

