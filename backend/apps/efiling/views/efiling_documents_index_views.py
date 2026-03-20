from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from apps.core.models import Efiling, EfilingDocumentsIndex
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

        if efiling_id is not None:
            filing = Efiling.objects.filter(pk=efiling_id).first()
            if filing is not None:
                ensure_document_indexes_for_filing(filing)

        qs = EfilingDocumentsIndex.objects.select_related("document", "document__e_filing").all()
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ["true", "1"])
        if efiling_id is not None:
            qs = qs.filter(document__e_filing=efiling_id)
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
            instance = serializer.save(
                created_by=self.request.user if self.request.user.is_authenticated else None,
                updated_by=self.request.user if self.request.user.is_authenticated else None,
            )
            create_scrutiny_history(
                instance,
                comments=instance.comments or "Document review item created.",
                user=self.request.user if self.request.user.is_authenticated else None,
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

                instance.file_part_path = uploaded_file
                filing = instance.document.e_filing if instance.document else None
                scrutiny_status = (
                    EfilingDocumentsIndex.ScrutinyStatus.DRAFT
                    if filing and filing.is_draft
                    else EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
                )
                instance.scrutiny_status = scrutiny_status
                instance.is_compliant = False
                instance.is_new_for_scrutiny = bool(filing and not filing.is_draft)
                instance.last_resubmitted_at = timezone.now() if instance.is_new_for_scrutiny else None
                instance.updated_by = request.user if request.user.is_authenticated else None
                instance.save(
                    update_fields=[
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
                    instance,
                    comments="Document re-uploaded by advocate.",
                    user=request.user if request.user.is_authenticated else None,
                    scrutiny_status=instance.scrutiny_status,
                )
                if filing:
                    derive_filing_status(filing)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)

            kwargs["partial"] = partial
            response = super().update(request, *args, **kwargs)
            instance.refresh_from_db()

            if "scrutiny_status" in request.data or "comments" in request.data:
                if "scrutiny_status" not in request.data and not instance.scrutiny_status:
                    instance.scrutiny_status = EfilingDocumentsIndex.ScrutinyStatus.UNDER_SCRUTINY
                if instance.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED:
                    instance.is_compliant = True
                elif instance.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.REJECTED:
                    instance.is_compliant = False

                instance.is_new_for_scrutiny = False
                instance.last_reviewed_at = timezone.now()
                instance.updated_by = request.user if request.user.is_authenticated else None
                instance.save(
                    update_fields=[
                        "scrutiny_status",
                        "is_compliant",
                        "is_new_for_scrutiny",
                        "last_reviewed_at",
                        "updated_by",
                        "updated_at",
                    ]
                )

            create_scrutiny_history(
                instance,
                comments=request.data.get("comments", instance.comments),
                user=request.user if request.user.is_authenticated else None,
                scrutiny_status=request.data.get("scrutiny_status", instance.scrutiny_status),
            )
            if instance.document and instance.document.e_filing:
                derive_filing_status(instance.document.e_filing)
        return response

