from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import (
    CaseAccessRequest,
    Efiling,
    EfilingDocuments,
    EfilingDocumentsIndex,
    EfilerDocumentAccess,
    Vakalatnama,
)
from apps.efiling.notification_utils import create_notification
from apps.efiling.serializers.case_access_request_serializers import CaseAccessRequestSerializer


ADVOCATE_GROUPS = {"ADVOCATE", "API_ADVOCATE"}
SCRUTINY_GROUPS = {"SCRUTINY_OFFICER", "API_SCRUTINY_OFFICER"}


def _group_names(user) -> set[str]:
    if not getattr(user, "is_authenticated", False):
        return set()
    return set(user.groups.values_list("name", flat=True))


def _is_advocate(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if bool(_group_names(user) & ADVOCATE_GROUPS):
        return True
    return (getattr(user, "registration_type", "") or "").strip().lower() == "advocate"


def _is_scrutiny_officer(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    return bool(_group_names(user) & SCRUTINY_GROUPS)


def _advocate_display_name(user) -> str:
    full_name = ""
    if user is not None and hasattr(user, "get_full_name"):
        full_name = (user.get_full_name() or "").strip()
    if full_name:
        return full_name
    email = (getattr(user, "email", "") or "").strip()
    if email:
        return email
    username = (getattr(user, "username", "") or "").strip()
    if username:
        return username
    return "Advocate"


def _resolve_vakalatnama_anchor(e_filing: Efiling) -> tuple[int, int | None]:
    indexes = EfilingDocumentsIndex.objects.filter(
        document__e_filing=e_filing,
        is_active=True,
    ).select_related("document")
    vakalat_qs = indexes.filter(
        document_sequence__isnull=False,
    ).filter(
        models.Q(document__document_type__icontains="vakalat")
        | models.Q(document_part_name__icontains="vakalat")
    )
    anchor = vakalat_qs.exclude(
        document_part_name__istartswith="Vakalatnama - "
    ).order_by("document_sequence", "id").first()
    if anchor is None:
        anchor = vakalat_qs.order_by("document_sequence", "id").first()
    if anchor and anchor.document_sequence:
        return int(anchor.document_sequence), int(anchor.id)

    max_seq = (
        indexes.exclude(document_sequence__isnull=True)
        .order_by("-document_sequence")
        .values_list("document_sequence", flat=True)
        .first()
    )
    return (int(max_seq) if max_seq else 0) + 1, None


def _append_case_access_vakalatnama_to_case_files(
    *,
    req: CaseAccessRequest,
    approved_by,
) -> None:
    advocate_name = _advocate_display_name(req.advocate)
    sequence, parent_index_id = _resolve_vakalatnama_anchor(req.e_filing)
    part_name = f"Vakalatnama - {advocate_name}"

    document = EfilingDocuments.objects.create(
        e_filing=req.e_filing,
        e_filing_number=req.e_filing.e_filing_number,
        document_type="VAKALATNAMA",
        final_document=req.vakalatnama_document,
        filed_by=advocate_name,
    )
    EfilingDocumentsIndex.objects.create(
        document=document,
        document_part_name=part_name,
        file_part_path=req.vakalatnama_document,
        document_sequence=sequence,
        parent_document_index_id=parent_index_id,
        is_active=True,
        is_compliant=True,
        comments="Vakalatnama uploaded via approved case access request.",
        scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
        draft_scrutiny_status=None,
        draft_comments=None,
        draft_reviewed_at=None,
        is_new_for_scrutiny=False,
        last_resubmitted_at=None,
        last_reviewed_at=timezone.now(),
        created_by=approved_by if getattr(approved_by, "is_authenticated", False) else None,
        updated_by=approved_by if getattr(approved_by, "is_authenticated", False) else None,
    )


class CaseAccessRequestListCreateView(ListCreateAPIView):
    queryset = CaseAccessRequest.objects.select_related("advocate", "e_filing", "reviewed_by").all()
    serializer_class = CaseAccessRequestSerializer

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.order_by("-id")
        if _is_scrutiny_officer(user):
            status_filter = (self.request.query_params.get("status") or "").strip().upper()
            if status_filter:
                qs = qs.filter(status=status_filter)
            return qs
        if _is_advocate(user):
            return qs.filter(advocate=user)
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not _is_advocate(user):
            raise PermissionDenied("Only advocates can create case access requests.")

        obj = serializer.save(
            advocate=user,
            e_filing=serializer.validated_data["e_filing"],
            is_active=True,
        )


class CaseAccessRequestReviewView(APIView):
    def patch(self, request, pk: int, *args, **kwargs):
        user = request.user
        if not _is_scrutiny_officer(user):
            raise PermissionDenied("Only scrutiny officers can review case access requests.")

        req = CaseAccessRequest.objects.select_related("advocate", "e_filing").filter(pk=pk).first()
        if req is None:
            raise ValidationError({"detail": "Request not found."})
        if not req.is_active:
            raise ValidationError({"detail": "Request is inactive and cannot be reviewed."})
        if req.status != CaseAccessRequest.Status.PENDING:
            raise ValidationError({"detail": "Only pending requests can be reviewed."})

        decision = (request.data.get("status") or "").strip().upper()
        if decision not in {CaseAccessRequest.Status.APPROVED, CaseAccessRequest.Status.REJECTED}:
            raise ValidationError({"status": "Use APPROVED or REJECTED."})

        reason = (request.data.get("rejection_reason") or "").strip()
        now = timezone.now()
        with transaction.atomic():
            if decision == CaseAccessRequest.Status.APPROVED:
                vakalatnama = Vakalatnama.objects.create(
                    e_filing=req.e_filing,
                    e_filing_number=req.e_filing.e_filing_number,
                    vakalatnama_document=req.vakalatnama_document,
                )
                access = EfilerDocumentAccess.objects.create(
                    vakalatnama=vakalatnama,
                    e_filing=req.e_filing,
                    e_filing_number=req.e_filing.e_filing_number,
                    efiler=req.advocate,
                    accces_allowed_from=now,
                    access_provided_by=user,
                )
                _append_case_access_vakalatnama_to_case_files(req=req, approved_by=user)
                req.status = CaseAccessRequest.Status.APPROVED
                req.rejection_reason = ""
                req.approved_access = access
            else:
                if not reason:
                    raise ValidationError({"rejection_reason": "Rejection reason is required."})
                req.status = CaseAccessRequest.Status.REJECTED
                req.rejection_reason = reason

            req.reviewed_by = user
            req.reviewed_at = now
            req.save(
                update_fields=[
                    "status",
                    "rejection_reason",
                    "approved_access",
                    "reviewed_by",
                    "reviewed_at",
                    "updated_at",
                    "updated_by",
                ]
            )

        if decision == CaseAccessRequest.Status.APPROVED:
            message = f"Your case access request for {req.case_number} has been approved."
            notification_type = "scrutiny_accepted"
        else:
            message = f"Your case access request for {req.case_number} was rejected: {req.rejection_reason}"
            notification_type = "scrutiny_rejected"

        create_notification(
            role="advocate",
            notification_type=notification_type,
            message=message,
            e_filing=req.e_filing,
            link_url="/advocate/dashboard/efiling/case-access-requests",
        )
        return Response(CaseAccessRequestSerializer(req, context={"request": request}).data)


class CaseAccessRequestReapplyView(APIView):
    def post(self, request, pk: int, *args, **kwargs):
        user = request.user
        if not _is_advocate(user):
            raise PermissionDenied("Only advocates can reapply.")

        previous = (
            CaseAccessRequest.objects.select_related("e_filing")
            .filter(pk=pk, advocate=user, is_active=True)
            .first()
        )
        if previous is None:
            raise ValidationError({"detail": "Request not found."})
        if previous.status != CaseAccessRequest.Status.REJECTED:
            raise ValidationError({"detail": "Only rejected requests can be reapplied."})

        pending_exists = CaseAccessRequest.objects.filter(
            advocate=user,
            e_filing=previous.e_filing,
            status=CaseAccessRequest.Status.PENDING,
            is_active=True,
        ).exists()
        if pending_exists:
            raise ValidationError({"detail": "A pending request already exists for this case."})

        uploaded = request.FILES.get("vakalatnama_document")
        if uploaded is None:
            uploaded = previous.vakalatnama_document
        if not uploaded:
            raise ValidationError({"vakalatnama_document": "Upload vakalatnama document to reapply."})

        obj = CaseAccessRequest.objects.create(
            advocate=user,
            e_filing=previous.e_filing,
            case_number=previous.case_number,
            vakalatnama_document=uploaded,
            status=CaseAccessRequest.Status.PENDING,
            resubmission_of=previous,
        )
        return Response(
            CaseAccessRequestSerializer(obj, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CaseAccessCaseSearchView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not _is_advocate(user):
            raise PermissionDenied("Only advocates can search case access candidates.")

        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response({"items": []}, status=status.HTTP_200_OK)

        # Smart search source:
        # - registered/non-draft filings only
        # - exclude advocate's own filings
        # - exclude filings where advocate already has access
        own_ids = Efiling.objects.filter(created_by=user).values_list("id", flat=True)
        accessible_ids = EfilerDocumentAccess.objects.filter(
            efiler=user,
            is_active=True,
        ).values_list("e_filing_id", flat=True)

        rows = (
            Efiling.objects.filter(is_draft=False, case_number__icontains=q)
            .exclude(id__in=own_ids)
            .exclude(id__in=accessible_ids)
            .exclude(case_number__isnull=True)
            .exclude(case_number__exact="")
            .order_by("-id")
            .values("id", "case_number", "e_filing_number", "petitioner_name")[:20]
        )
        return Response({"items": list(rows)}, status=status.HTTP_200_OK)
