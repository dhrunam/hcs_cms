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
from apps.core.models import Efiling, EfilingDocumentsIndex
from apps.efiling.serializers.efiling_document_index import EfilingDocumentsIndexSerializer

from .models import (
    CourtroomDocumentAnnotation,
    CourtroomForward,
    CourtroomJudgeDecision,
    JUDGE_GROUP_CJ,
    JUDGE_GROUP_J1,
    JUDGE_GROUP_J2,
)
from .serializers import (
    CourtroomCaseDocumentAnnotationUpsertSerializer,
    CourtroomDecisionSerializer,
    CourtroomDocumentAnnotationSerializer,
    CourtroomForwardSerializer,
    CourtroomPendingCaseSerializer,
)


BENCH_TO_REQUIRED_GROUPS: Dict[str, Sequence[str]] = {
    "CJ": (JUDGE_GROUP_CJ,),
    "Judge1": (JUDGE_GROUP_J1,),
    "Judge2": (JUDGE_GROUP_J2,),
    "CJ+Judge1": (JUDGE_GROUP_CJ, JUDGE_GROUP_J1),
    "CJ+Judge2": (JUDGE_GROUP_CJ, JUDGE_GROUP_J2),
    "Judge1+Judge2": (JUDGE_GROUP_J1, JUDGE_GROUP_J2),
    "CJ+Judge1+Judge2": (JUDGE_GROUP_CJ, JUDGE_GROUP_J1, JUDGE_GROUP_J2),
}

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
    req = BENCH_TO_REQUIRED_GROUPS.get(bench_key)
    if not req:
        raise ValidationError({"bench_key": f"Unknown bench_key={bench_key}."})
    return req


def _judge_can_view_forward(user_groups: Set[str], bench_key: str) -> bool:
    req = set(_bench_required_groups(bench_key))
    return bool(user_groups & req)


class CourtroomForwardView(APIView):
    """
    Listing Officer: forward selected efilings to judges.
    Input: { forwarded_for_date, bench_key, efiling_ids: [...] }
    """

    def post(self, request, *args, **kwargs):
        payload = CourtroomForwardSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        # Listing-officer auth is not implemented yet; allow for now (front-end will handle flow).
        user = getattr(request, "user", None)

        forwarded_for_date = payload.validated_data["forwarded_for_date"]
        bench_key = payload.validated_data["bench_key"]
        efiling_ids = payload.validated_data["efiling_ids"]

        if not efiling_ids:
            return Response({"updated": 0}, status=drf_status.HTTP_200_OK)

        ef_qs = Efiling.objects.filter(id__in=efiling_ids).only("id", "bench")
        found_ids = set(ef_qs.values_list("id", flat=True))
        missing = [eid for eid in efiling_ids if eid not in found_ids]
        if missing:
            raise ValidationError({"efiling_ids": f"Not found: {missing}"})

        # Enforce bench consistency to avoid forwarding cases under a mismatched bench.
        ef_by_id = {e.id: e for e in ef_qs}
        errors: List[dict] = []
        valid_ids: List[int] = []
        for eid in efiling_ids:
            filing = ef_by_id[eid]
            if (filing.bench or "") != bench_key:
                errors.append(
                    {
                        "efiling_id": eid,
                        "detail": f"bench mismatch (current={filing.bench or '-'}, expected={bench_key})",
                    }
                )
                continue
            valid_ids.append(eid)

        # Upsert forward rows for bench/date+efiling.
        updated = 0
        for eid in valid_ids:
            obj, created = CourtroomForward.objects.update_or_create(
                efiling_id=eid,
                forwarded_for_date=forwarded_for_date,
                bench_key=bench_key,
                defaults={"forwarded_by": user if getattr(user, "is_authenticated", False) else None},
            )
            updated += 1

        return Response(
            {
                "updated": updated,
                "skipped": len(errors),
                "errors": errors,
            },
            status=drf_status.HTTP_200_OK,
        )


class CourtroomPendingCasesView(APIView):
    """
    Judge: list all pending forwarded cases for a forwarded_for_date where judge role is included in bench_key.
    """

    def get(self, request, *args, **kwargs):
        user = _assert_judge(request)
        forwarded_for_date = request.query_params.get("forwarded_for_date")
        if not forwarded_for_date:
            raise ValidationError({"forwarded_for_date": "Required."})

        forwarded_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
        user_groups = _user_judge_groups(user)

        forwards = CourtroomForward.objects.filter(forwarded_for_date=forwarded_date).select_related("efiling")
        pending_for_listing: List[dict] = []
        pending_for_causelist: List[dict] = []
        for f in forwards:
            if _judge_can_view_forward(user_groups, f.bench_key):
                decision = (
                    CourtroomJudgeDecision.objects.filter(
                        judge_user=user,
                        efiling_id=f.efiling_id,
                        forwarded_for_date=forwarded_date,
                    )
                    .only("approved", "listing_date")
                    .first()
                )
                item = {
                    "efiling_id": f.efiling_id,
                    "case_number": f.efiling.case_number,
                    "bench_key": f.bench_key,
                    "judge_decision": (decision.approved if decision else None),
                    "judge_listing_date": (str(decision.listing_date) if decision and decision.listing_date else None),
                }
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
        if not forwarded_for_date:
            raise ValidationError({"forwarded_for_date": "Required."})

        forwarded_date = timezone.datetime.fromisoformat(forwarded_for_date).date()
        user_groups = _user_judge_groups(user)

        forward = (
            CourtroomForward.objects.filter(
                efiling_id=efiling_id, forwarded_for_date=forwarded_date
            )
            .order_by("-id")
            .first()
        )
        if not forward:
            raise ValidationError({"detail": "Case not forwarded for this date."})
        if not _judge_can_view_forward(user_groups, forward.bench_key):
            raise ValidationError({"detail": "Not authorized for this case/bench."})

        doc_indexes_qs = EfilingDocumentsIndex.objects.filter(
            document__e_filing_id=efiling_id, is_active=True
        ).select_related("document", "document__e_filing").order_by("id")

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
        allowed_bench_keys = [
            bench_key
            for bench_key, req_groups in BENCH_TO_REQUIRED_GROUPS.items()
            if set(req_groups) & user_groups
        ]
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
    Judge: save approve/reject + listing_date for a forwarded case.
    """

    def post(self, request, *args, **kwargs):
        user = _assert_judge(request)
        payload = CourtroomDecisionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        efiling_id = payload.validated_data["efiling_id"]
        forwarded_for_date = payload.validated_data["forwarded_for_date"]
        listing_date = payload.validated_data["listing_date"]
        approved = payload.validated_data["approved"]
        decision_notes = payload.validated_data.get("decision_notes")

        # Ensure there is a forward row and judge is allowed.
        forward = (
            CourtroomForward.objects.filter(efiling_id=efiling_id, forwarded_for_date=forwarded_for_date)
            .order_by("-id")
            .first()
        )
        if not forward:
            raise ValidationError({"detail": "Case not forwarded for this date."})

        user_groups = _user_judge_groups(user)
        if not _judge_can_view_forward(user_groups, forward.bench_key):
            raise ValidationError({"detail": "Not authorized for this case/bench."})

        obj, _created = CourtroomJudgeDecision.objects.update_or_create(
            judge_user=user,
            efiling_id=efiling_id,
            forwarded_for_date=forwarded_for_date,
            defaults={
                "listing_date": listing_date,
                "approved": approved,
                "decision_notes": decision_notes,
            },
        )

        return Response(
            {"efiling_id": efiling_id, "approved": obj.approved, "listing_date": str(obj.listing_date)},
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

