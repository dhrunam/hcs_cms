from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Set

from django.contrib.auth.models import Group, AnonymousUser
from django.db.models import Q
from django.utils import timezone
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from apps.accounts.models import User
from apps.core.bench_config import (
    get_bench_configurations,
    get_bench_configuration_for_stored_value,
    get_required_judge_groups,
)
from apps.core.models import Efiling, EfilingCaseDetails, EfilingDocumentsIndex, EfilingLitigant
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.efiling.serializers.efiling_document_index import EfilingDocumentsIndexSerializer

from .models import (
    CourtroomDecisionRequestedDocument,
    CourtroomDocumentAnnotation,
    CourtroomJudgeDecision,
    JUDGE_GROUP_CJ,
    JUDGE_GROUP_J1,
    JUDGE_GROUP_J2,
)
from apps.reader.models import CourtroomForward, CourtroomForwardDocument
from .serializers import (
    CourtroomCaseDocumentAnnotationUpsertSerializer,
    CourtroomDecisionSerializer,
    CourtroomDocumentAnnotationSerializer,
    CourtroomPendingCaseSerializer,
)

_DUMMY_TOKEN_TO_DUMMY_EMAIL: Dict[str, str] = {
    "judge_cj_dummy_token": "dummy_judge_cj@hcs.local",
    "judge_j1_dummy_token": "dummy_judge_j1@hcs.local",
    "judge_j2_dummy_token": "dummy_judge_j2@hcs.local",
}


def _auth_header_token(request) -> Optional[str]:
    auth = request.META.get("HTTP_AUTHORIZATION") or ""
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def _resolve_judge_user(request) -> User:
    """
    Resolve a Django User for judge endpoints.

    - If `request.user` is authenticated, use it.
    - Otherwise (dev dummy logins), map known dummy tokens to pre-created dummy judge users.
    """
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user

    token = _auth_header_token(request)
    if not token:
        raise ValidationError({"detail": "Authentication required."})

    email = _DUMMY_TOKEN_TO_DUMMY_EMAIL.get(token)
    if not email:
        raise ValidationError({"detail": "Authentication required."})

    UserModel = get_user_model()
    try:
        return UserModel.objects.get(email=email)
    except UserModel.DoesNotExist as e:
        raise ValidationError({"detail": "Judge user not provisioned."}) from e


def _user_judge_groups(user: User) -> Set[str]:
    if not user:
        return set()
    return set(
        user.groups.filter(name__in={JUDGE_GROUP_CJ, JUDGE_GROUP_J1, JUDGE_GROUP_J2}).values_list(
            "name", flat=True
        )
    )


def _assert_judge(request) -> User:
    user = _resolve_judge_user(request)
    if not _user_judge_groups(user):
        raise ValidationError({"detail": "Not authorized as judge."})
    return user


def _bench_required_groups(bench_key: str) -> Sequence[str]:
    req = get_required_judge_groups(bench_key)
    if not req:
        raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})
    return req


def _judge_can_view_forward(user_groups: Set[str], bench_key: str) -> bool:
    req = set(_bench_required_groups(bench_key))
    return bool(user_groups & req)


def _allowed_bench_keys_for_judge(user_groups: Set[str]) -> list[str]:
    allowed_bench_keys: list[str] = []
    for bench in get_bench_configurations():
        if set(bench.judge_groups) & user_groups:
            allowed_bench_keys.append(bench.bench_key)
    return allowed_bench_keys


def _get_display_bench_for_efiling(
    efiling: Efiling | None,
    fallback_bench_key: str,
) -> tuple[str, str]:
    bench_config = get_bench_configuration_for_stored_value(
        getattr(efiling, "bench", None),
    )
    if bench_config:
        return bench_config.bench_key, bench_config.label
    return fallback_bench_key, fallback_bench_key


class CourtroomPendingCasesView(APIView):
    """
    Judge: list all pending forwarded cases for a forwarded_for_date where judge role is included in bench_key.
    """

    def get(self, request, *args, **kwargs):
        user = _assert_judge(request)
        forwarded_for_date = request.query_params.get("forwarded_for_date")
        if forwarded_for_date:
            forwarded_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
            forwards = (
                CourtroomForward.objects.filter(forwarded_for_date=forwarded_date)
                .select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-id")
            )
        else:
            # Fallback for UI: if no date is provided, show latest forwards first.
            forwarded_date = None
            forwards = (
                CourtroomForward.objects.all()
                .select_related("efiling")
                .prefetch_related("efiling__litigants")
                .order_by("-forwarded_for_date", "-id")
            )
        user_groups = _user_judge_groups(user)
        pending_for_listing: List[dict] = []
        pending_for_causelist: List[dict] = []
        seen: Set[int] = set()
        for f in forwards:
            if f.efiling_id in seen:
                continue
            if _judge_can_view_forward(user_groups, f.bench_key):
                seen.add(f.efiling_id)
                display_bench_key, display_bench_label = (
                    _get_display_bench_for_efiling(
                        f.efiling,
                        f.bench_key,
                    )
                )
                decision = (
                    CourtroomJudgeDecision.objects.filter(
                        judge_user=user,
                        efiling_id=f.efiling_id,
                        forwarded_for_date=f.forwarded_for_date,
                    )
                    .only("approved", "listing_date")
                    .first()
                )
                item = {
                    "efiling_id": f.efiling_id,
                    "e_filing_number": getattr(f.efiling, "e_filing_number", None),
                    "case_number": f.efiling.case_number,
                    "bench_key": display_bench_key,
                    "bench_label": display_bench_label,
                    "forward_bench_key": f.bench_key,
                    "petitioner_name": getattr(f.efiling, "petitioner_name", None),
                    "petitioner_vs_respondent": (getattr(f.efiling, "petitioner_name", None) or "").strip() or build_petitioner_vs_respondent(
                        f.efiling,
                        fallback_petitioner_name=getattr(f.efiling, "petitioner_name", None) or "",
                    ),
                    "listing_summary": f.listing_summary,
                    "selected_document_count": f.selected_documents.count(),
                    "requested_document_count": 0,
                    "requested_documents": [],
                    "judge_decision": (decision.approved if decision else None),
                    "judge_decision_status": (
                        decision.status if decision else None
                    ),
                    "judge_listing_date": (str(decision.listing_date) if decision and decision.listing_date else None),
                    "forwarded_for_date": f.forwarded_for_date.isoformat(),
                }
                if decision:
                    req_docs = list(
                        decision.requested_documents.select_related("efiling_document_index").values(
                            "efiling_document_index_id",
                            "efiling_document_index__document_part_name",
                            "efiling_document_index__document__document_type",
                        )
                    )
                    item["requested_document_count"] = len(req_docs)
                    item["requested_documents"] = [
                        {
                            "document_index_id": r["efiling_document_index_id"],
                            "document_part_name": r.get("efiling_document_index__document_part_name"),
                            "document_type": r.get("efiling_document_index__document__document_type"),
                        }
                        for r in req_docs
                    ]
                if decision and decision.approved:
                    pending_for_causelist.append(item)
                else:
                    pending_for_listing.append(item)

        return Response(
            {
                "pending_for_listing": pending_for_listing,
                "pending_for_causelist": pending_for_causelist,
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomCaseDocumentsView(APIView):
    """
    Judge: get document index items for the case plus current annotation_text for this judge.
    """

    def get(self, request, efiling_id: int, *args, **kwargs):
        user = _assert_judge(request)
        forwarded_for_date = request.query_params.get("forwarded_for_date")
        user_groups = _user_judge_groups(user)
        allowed_bench_keys = _allowed_bench_keys_for_judge(user_groups)
        forward = None
        if forwarded_for_date:
            forwarded_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
            forward = (
                CourtroomForward.objects.filter(
                    efiling_id=efiling_id,
                    forwarded_for_date=forwarded_date,
                    bench_key__in=allowed_bench_keys,
                )
                .order_by("-id")
                .first()
            )

        # Fallback to latest forward for this case so UI does not fail
        # when client-provided date is stale.
        if not forward:
            forward = (
                CourtroomForward.objects.filter(
                    efiling_id=efiling_id,
                    bench_key__in=allowed_bench_keys,
                )
                .order_by("-forwarded_for_date", "-id")
                .first()
            )
        if not forward:
            raise ValidationError({"detail": "Case not forwarded."})
        if not _judge_can_view_forward(user_groups, forward.bench_key):
            raise ValidationError({"detail": "Not authorized for this case/bench."})

        requested_only = str(request.query_params.get("requested_only", "")).strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }

        doc_indexes_qs = EfilingDocumentsIndex.objects.filter(
            document__e_filing_id=efiling_id, is_active=True
        ).select_related("document", "document__e_filing").order_by("id")
        if requested_only:
            decision = (
                CourtroomJudgeDecision.objects.filter(
                    judge_user=user,
                    efiling_id=efiling_id,
                    forwarded_for_date=forward.forwarded_for_date,
                )
                .order_by("-id")
                .first()
            )
            requested_ids = (
                list(
                    decision.requested_documents.values_list(
                        "efiling_document_index_id", flat=True
                    )
                )
                if decision
                else []
            )
            if requested_ids:
                doc_indexes_qs = doc_indexes_qs.filter(id__in=requested_ids)

        serializer = EfilingDocumentsIndexSerializer(doc_indexes_qs, many=True, context={"request": request})
        doc_items = serializer.data

        existing = CourtroomDocumentAnnotation.objects.filter(
            judge_user=user, efiling_document_index__in=doc_indexes_qs
        )
        anno_map = {a.efiling_document_index_id: a for a in existing}

        for item in doc_items:
            idx_id = item.get("id")
            anno = anno_map.get(idx_id)
            item["annotation_text"] = anno.annotation_text if anno else (item.get("draft_comments") or item.get("comments") or None)

        return Response({"items": doc_items}, status=drf_status.HTTP_200_OK)


class CourtroomCaseSummaryView(APIView):
    """
    Judge: get case summary details only (no document payload).
    """

    def get(self, request, efiling_id: int, *args, **kwargs):
        user = _assert_judge(request)
        forwarded_for_date = request.query_params.get("forwarded_for_date")
        user_groups = _user_judge_groups(user)
        allowed_bench_keys = _allowed_bench_keys_for_judge(user_groups)
        if not allowed_bench_keys:
            raise ValidationError({"detail": "Not authorized as judge."})

        forward_qs = CourtroomForward.objects.filter(
            efiling_id=efiling_id,
            bench_key__in=allowed_bench_keys,
        )
        if forwarded_for_date:
            forwarded_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
            forward_qs = forward_qs.filter(forwarded_for_date=forwarded_date)

        forward = forward_qs.order_by("-forwarded_for_date", "-id").first()
        if not forward:
            raise ValidationError({"detail": "Case not forwarded for this judge/date."})

        filing = (
            Efiling.objects.filter(id=efiling_id)
            .prefetch_related("litigants")
            .first()
        )
        if not filing:
            raise ValidationError({"detail": "Case not found."})
        display_bench_key, display_bench_label = _get_display_bench_for_efiling(
            filing,
            forward.bench_key,
        )

        case_detail = (
            EfilingCaseDetails.objects.filter(e_filing_id=efiling_id)
            .select_related("dispute_state", "dispute_district")
            .order_by("-id")
            .first()
        )
        litigants = list(
            EfilingLitigant.objects.filter(e_filing_id=efiling_id)
            .only("name", "is_petitioner", "sequence_number")
            .order_by("is_petitioner", "sequence_number", "id")
            .values("id", "name", "is_petitioner", "sequence_number")
        )
        selected_documents = list(
            forward.selected_documents.select_related("efiling_document_index")
            .values(
                "efiling_document_index_id",
                "efiling_document_index__document_part_name",
                "efiling_document_index__document__document_type",
                "efiling_document_index__file_part_path",
            )
        )
        latest_decision = (
            CourtroomJudgeDecision.objects.filter(
                judge_user=user,
                efiling_id=efiling_id,
                forwarded_for_date=forward.forwarded_for_date,
            )
            .order_by("-id")
            .first()
        )

        return Response(
            {
                "efiling_id": filing.id,
                "case_number": filing.case_number,
                "e_filing_number": filing.e_filing_number,
                "petitioner_name": filing.petitioner_name,
                "petitioner_vs_respondent": (filing.petitioner_name or "").strip() or build_petitioner_vs_respondent(
                    filing, fallback_petitioner_name=filing.petitioner_name or ""
                ),
                "petitioner_contact": filing.petitioner_contact,
                "bench_key": display_bench_key,
                "bench_label": display_bench_label,
                "forward_bench_key": forward.bench_key,
                "forwarded_for_date": forward.forwarded_for_date.isoformat(),
                "listing_summary": forward.listing_summary,
                "selected_documents": [
                    {
                        "document_index_id": d["efiling_document_index_id"],
                        "document_part_name": d.get("efiling_document_index__document_part_name"),
                        "document_type": d.get("efiling_document_index__document__document_type"),
                        "file_url": d.get("efiling_document_index__file_part_path"),
                    }
                    for d in selected_documents
                ],
                "judge_decision": (
                    {
                        "status": latest_decision.status,
                        "approved": latest_decision.approved,
                        "listing_date": latest_decision.listing_date.isoformat()
                        if latest_decision.listing_date
                        else None,
                        "decision_notes": latest_decision.decision_notes,
                        "requested_documents": [
                            {
                                "document_index_id": rd["efiling_document_index_id"],
                                "document_part_name": rd.get("efiling_document_index__document_part_name"),
                                "document_type": rd.get("efiling_document_index__document__document_type"),
                            }
                            for rd in (
                                latest_decision.requested_documents.select_related("efiling_document_index").values(
                                    "efiling_document_index_id",
                                    "efiling_document_index__document_part_name",
                                    "efiling_document_index__document__document_type",
                                )
                                if latest_decision
                                else []
                            )
                        ],
                    }
                    if latest_decision
                    else None
                ),
                "litigants": litigants,
                "case_details": {
                    "cause_of_action": getattr(case_detail, "cause_of_action", None) if case_detail else None,
                    "date_of_cause_of_action": (
                        case_detail.date_of_cause_of_action.isoformat()
                        if case_detail and getattr(case_detail, "date_of_cause_of_action", None)
                        else None
                    ),
                    "dispute_state": (
                        getattr(getattr(case_detail, "dispute_state", None), "state", None)
                        if case_detail
                        else None
                    ),
                    "dispute_district": (
                        getattr(getattr(case_detail, "dispute_district", None), "district", None)
                        if case_detail
                        else None
                    ),
                    "dispute_taluka": getattr(case_detail, "dispute_taluka", None) if case_detail else None,
                },
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomDocumentAnnotationView(APIView):
    """
    Judge: upsert annotation text for a document index.
    """

    def post(self, request, *args, **kwargs):
        user = _assert_judge(request)
        payload = CourtroomCaseDocumentAnnotationUpsertSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        doc_index_id = payload.validated_data["efiling_document_index_id"]
        annotation_text = payload.validated_data.get("annotation_text")

        # Authorization: only allow annotating documents belonging to efilings
        # that were forwarded for a bench where this judge role applies.
        doc_index = (
            EfilingDocumentsIndex.objects.select_related("document")
            .filter(id=doc_index_id)
            .first()
        )
        if not doc_index or not doc_index.document_id:
            raise ValidationError({"efiling_document_index_id": "Invalid document index."})

        user_groups = _user_judge_groups(user)
        allowed_bench_keys = _allowed_bench_keys_for_judge(user_groups)
        if not CourtroomForward.objects.filter(
            efiling_id=doc_index.document.e_filing_id,
            bench_key__in=allowed_bench_keys,
        ).exists():
            raise ValidationError({"detail": "Not authorized to annotate this document."})

        ann, _ = CourtroomDocumentAnnotation.objects.update_or_create(
            judge_user=user,
            efiling_document_index_id=doc_index_id,
            defaults={"annotation_text": annotation_text},
        )
        return Response(
            {"efiling_document_index": doc_index_id, "annotation_text": ann.annotation_text},
            status=drf_status.HTTP_200_OK,
        )


class CourtroomDecisionView(APIView):
    """
    Judge: save a decision for a forwarded case and return it to reader flow.
    """

    def post(self, request, *args, **kwargs):
        user = _assert_judge(request)
        payload = CourtroomDecisionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        efiling_id = payload.validated_data["efiling_id"]
        forwarded_for_date = payload.validated_data["forwarded_for_date"]
        status = CourtroomJudgeDecision.DecisionStatus.APPROVED
        requested_document_index_ids = payload.validated_data.get("requested_document_index_ids") or []
        approved = True
        decision_notes = payload.validated_data.get("decision_notes")
        user_groups = _user_judge_groups(user)
        allowed_bench_keys = _allowed_bench_keys_for_judge(user_groups)

        # Ensure there is a forward row and judge is allowed.
        forward = (
            CourtroomForward.objects.filter(
                efiling_id=efiling_id,
                forwarded_for_date=forwarded_for_date,
                bench_key__in=allowed_bench_keys,
            )
            .order_by("-id")
            .first()
        )
        if not forward:
            raise ValidationError({"detail": "Case not forwarded for this date."})

        if not _judge_can_view_forward(user_groups, forward.bench_key):
            raise ValidationError({"detail": "Not authorized for this case/bench."})

        obj, _created = CourtroomJudgeDecision.objects.update_or_create(
            judge_user=user,
            efiling_id=efiling_id,
            forwarded_for_date=forwarded_for_date,
            defaults={
                "status": status,
                "approved": approved,
                "decision_notes": decision_notes,
            },
        )
        valid_req_doc_ids = set()
        if requested_document_index_ids:
            valid_req_doc_ids = set(
                EfilingDocumentsIndex.objects.filter(
                    id__in=requested_document_index_ids,
                    document__e_filing_id=efiling_id,
                ).values_list("id", flat=True)
            )
        CourtroomDecisionRequestedDocument.objects.filter(judge_decision=obj).exclude(
            efiling_document_index_id__in=valid_req_doc_ids
        ).delete()
        for doc_id in valid_req_doc_ids:
            CourtroomDecisionRequestedDocument.objects.get_or_create(
                judge_decision=obj,
                efiling_document_index_id=doc_id,
            )

        return Response(
            {
                "efiling_id": efiling_id,
                "status": obj.status,
                "approved": obj.approved,
                "requested_document_count": len(valid_req_doc_ids),
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomApprovedLookupView(APIView):
    """
    Listing Officer: bulk lookup which efilings are judge-approved for a given bench_key and cause_list_date.
    GET is used with query params as per plan.
    """

    def get(self, request, *args, **kwargs):
        cause_list_date = request.query_params.get("cause_list_date")
        bench_key = request.query_params.get("bench_key")
        if not cause_list_date or not bench_key:
            raise ValidationError({"cause_list_date": "Required.", "bench_key": "Required."})

        cld = timezone.datetime.fromisoformat(cause_list_date).date()
        required_groups = _bench_required_groups(bench_key)

        forwarded_ids = set(
            CourtroomForward.objects.filter(
                bench_key=bench_key,
                forwarded_for_date=cld,
            ).values_list("efiling_id", flat=True)
        )
        if not forwarded_ids:
            return Response({"efiling_ids": []}, status=drf_status.HTTP_200_OK)

        # Strict rule: each required group must have at least one approving judge
        # for the same forwarded_for_date and same listing_date.
        group_to_ids: List[Set[int]] = []
        for group_name in required_groups:
            ids = set(
                CourtroomJudgeDecision.objects.filter(
                    judge_user__groups__name=group_name,
                    efiling_id__in=forwarded_ids,
                    forwarded_for_date=cld,
                    listing_date=cld,
                    approved=True,
                ).values_list("efiling_id", flat=True)
            )
            group_to_ids.append(ids)

        eligible_ids: Set[int] = set.intersection(*group_to_ids) if group_to_ids else set()

        return Response({"efiling_ids": sorted(list(eligible_ids))}, status=drf_status.HTTP_200_OK)


class CourtroomDecisionCalendarView(APIView):
    """
    Judge: list all of my decisions for calendar rendering.
    """

    def get(self, request, *args, **kwargs):
        user = _assert_judge(request)
        rows = (
            CourtroomJudgeDecision.objects.filter(judge_user=user)
            .select_related("efiling")
            .prefetch_related("efiling__litigants")
            .order_by("-listing_date", "-forwarded_for_date", "-id")
        )
        items = []
        for row in rows:
            ef = row.efiling
            items.append(
                {
                    "efiling_id": row.efiling_id,
                    "e_filing_number": getattr(ef, "e_filing_number", None),
                    "case_number": row.efiling.case_number,
                    "petitioner_name": getattr(ef, "petitioner_name", None),
                    "petitioner_vs_respondent": (getattr(ef, "petitioner_name", None) or "").strip() or build_petitioner_vs_respondent(
                        ef, fallback_petitioner_name=getattr(ef, "petitioner_name", None) or ""
                    ),
                    "status": row.status,
                    "approved": row.approved,
                    "listing_date": row.listing_date.isoformat()
                    if row.listing_date
                    else None,
                    "forwarded_for_date": row.forwarded_for_date.isoformat()
                    if row.forwarded_for_date
                    else None,
                    "decision_notes": row.decision_notes,
                }
            )
        return Response({"items": items}, status=drf_status.HTTP_200_OK)




