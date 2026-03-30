from __future__ import annotations

from typing import Any, Dict, List, Sequence, Set

from django.core.files.base import ContentFile
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date as date_type
from django.utils.text import slugify
from rest_framework import status as drf_status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Efiling
from apps.core.models import EfilerDocumentAccess, EfilingCaseDetails, EfilingLitigant
from apps.accounts.models import User
from apps.judge.models import CourtroomForward, CourtroomJudgeDecision
from apps.listing.models import CauseList, CauseListEntry
from apps.listing.pdf_service import CauseListRow, generate_cause_list_pdf_bytes
from apps.listing.serializers import (
    CauseListDraftEntrySerializer,
    CauseListDraftSaveSerializer,
    AssignBenchesSerializer,
    CauseListPublishedSerializer,
    CauseListPublishSerializer,
    LatestCauseListLookupSerializer,
    NextCauseListLookupSerializer,
)

from django.db.models import Prefetch, Q


BENCH_TO_REQUIRED_GROUPS: Dict[str, Sequence[str]] = {
    "CJ": ("JUDGE_CJ",),
    "Judge1": ("JUDGE_J1",),
    "Judge2": ("JUDGE_J2",),
    "CJ+Judge1": ("JUDGE_CJ", "JUDGE_J1"),
    "CJ+Judge2": ("JUDGE_CJ", "JUDGE_J2"),
    "Judge1+Judge2": ("JUDGE_J1", "JUDGE_J2"),
    "CJ+Judge1+Judge2": ("JUDGE_CJ", "JUDGE_J1", "JUDGE_J2"),
}


def _judge_approved_efiling_ids(cause_list_date: str, bench_key: str) -> Set[int]:
    """
    Returns efiling_ids that are approved by ALL required judge groups for this bench_key and date.
    """
    cld: date_type
    try:
        cld = timezone.datetime.fromisoformat(str(cause_list_date)).date()
    except Exception as e:
        raise ValidationError({"cause_list_date": f"Invalid date: {cause_list_date}"}) from e

    required_groups = BENCH_TO_REQUIRED_GROUPS.get(bench_key)
    if not required_groups:
        return set()

    forwarded_ids = set(
        CourtroomForward.objects.filter(
            bench_key=bench_key,
            forwarded_for_date=cld,
        ).values_list("efiling_id", flat=True)
    )
    if not forwarded_ids:
        return set()

    group_to_ids: List[Set[int]] = []
    for group_name in required_groups:
        # Strict eligibility: every required judge-group must approve the SAME listing date
        # (equal to selected cause_list_date) for the SAME forwarded date.
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

    return set.intersection(*group_to_ids) if group_to_ids else set()


def _main_parties_for_filing(filing: Efiling) -> str:
    qs = (
        EfilingLitigant.objects.filter(e_filing=filing)
        .only("name", "is_petitioner", "sequence_number")
        .order_by("is_petitioner", "sequence_number", "id")
    )
    petitioners = [x.name for x in qs if x.is_petitioner and x.name]
    respondents = [x.name for x in qs if (not x.is_petitioner) and x.name]

    pet = ", ".join(petitioners) if petitioners else (filing.petitioner_name or "")
    resp = ", ".join(respondents) if respondents else ""

    pet = pet.strip() or "-"
    resp = resp.strip() or "-"
    return f"{pet}\nVs\n{resp}"


def _advocates_for_filing(filing: Efiling) -> tuple[str, str]:
    accesses = (
        EfilerDocumentAccess.objects.filter(e_filing=filing)
        .select_related("efiler")
        .only("id", "efiler__first_name", "efiler__last_name", "efiler__email")
        .order_by("id")
    )
    names: List[str] = []
    for a in accesses:
        u = getattr(a, "efiler", None)
        if not u:
            continue
        full = (u.get_full_name() or "").strip()
        names.append(full if full else (getattr(u, "email", None) or "").strip())

    names = [n for n in names if n]
    petitioner_adv = "\n".join(names) if names else "-"
    respondent_adv = "-"
    return petitioner_adv, respondent_adv


class CauseListDraftPreviewView(APIView):
    """
    Listing Officer: preview the draft cause list selection.
    Returns all accepted cases for `bench_key` with preselected `included=True`.
    """

    def get(self, request, *args, **kwargs):
        cause_list_date = request.query_params.get("cause_list_date")
        bench_key = request.query_params.get("bench_key")

        if not cause_list_date or not bench_key:
            raise ValidationError({"detail": "cause_list_date and bench_key are required."})

        draft = (
            CauseList.objects.filter(
                cause_list_date=cause_list_date,
                bench_key=bench_key,
                status=CauseList.CauseListStatus.DRAFT,
            )
            .order_by("-id")
            .first()
        )

        # Auto preselect all accepted filings for this bench_key.
        approved_only_raw = request.query_params.get("approved_only", "true")
        approved_only = approved_only_raw.strip().lower() in {"true", "1", "yes", "y"}

        if approved_only:
            approved_ids = _judge_approved_efiling_ids(cause_list_date, bench_key)
            accepted = (
                Efiling.objects.filter(
                    id__in=approved_ids,
                    is_draft=False,
                    status="ACCEPTED",
                    bench=bench_key,
                )
                .order_by("id")
                .all()
            )
        else:
            accepted = (
                Efiling.objects.filter(
                    is_draft=False,
                    status="ACCEPTED",
                    bench=bench_key,
                )
                .order_by("id")
                .all()
            )

        existing_entries = {}
        if draft:
            qs = CauseListEntry.objects.filter(cause_list=draft).only("efiling_id", "included", "serial_no")
            existing_entries = {row.efiling_id: row for row in qs}

        items: List[Dict[str, Any]] = []
        for idx, filing in enumerate(accepted, start=1):
            existing = existing_entries.get(filing.id)
            items.append(
                {
                    "efiling_id": filing.id,
                    "case_number": filing.case_number,
                    "included": bool(existing.included) if existing else True,
                    "serial_no": existing.serial_no if existing and existing.serial_no is not None else idx,
                }
            )

        return Response(
            {
                "cause_list_id": draft.id if draft else None,
                "cause_list_date": cause_list_date,
                "bench_key": bench_key,
                "items": items,
            },
            status=drf_status.HTTP_200_OK,
        )


class CauseListDraftPdfPreviewView(APIView):
    """
    Listing Officer: generate a draft PDF preview (not published).

    - Uses DRAFT saved selections (included/serial_no) if available.
    - Otherwise defaults to include all ACCEPTED filings for the bench with sequential serials.
    """

    def get(self, request, *args, **kwargs):
        cause_list_date = request.query_params.get("cause_list_date")
        bench_key = request.query_params.get("bench_key")
        if not cause_list_date or not bench_key:
            raise ValidationError({"detail": "cause_list_date and bench_key are required."})

        draft = (
            CauseList.objects.filter(
                cause_list_date=cause_list_date,
                bench_key=bench_key,
                status=CauseList.CauseListStatus.DRAFT,
            )
            .order_by("-id")
            .first()
        )

        accepted = (
            Efiling.objects.filter(is_draft=False, status="ACCEPTED", bench=bench_key)
            .order_by("id")
            .all()
        )

        existing_entries: dict[int, CauseListEntry] = {}
        if draft:
            qs = (
                CauseListEntry.objects.filter(cause_list=draft)
                .only("efiling_id", "included", "serial_no")
                .all()
            )
            existing_entries = {row.efiling_id: row for row in qs}

        rows: List[CauseListRow] = []
        fallback_serial = 1
        for idx, filing in enumerate(accepted, start=1):
            existing = existing_entries.get(filing.id)
            included = bool(existing.included) if existing else True
            if not included:
                continue
            serial = (
                existing.serial_no
                if existing and existing.serial_no is not None
                else idx
            )
            if serial is None:
                serial = fallback_serial
                fallback_serial += 1

            main_parties = _main_parties_for_filing(filing)
            pet_adv, resp_adv = _advocates_for_filing(filing)
            rows.append(
                CauseListRow(
                    serial_no=int(serial),
                    case_number=filing.case_number or "",
                    main_parties=main_parties,
                    petitioner_advocates=pet_adv,
                    respondent_advocates=resp_adv,
                )
            )

        rows.sort(key=lambda r: (r.serial_no, r.case_number))
        # `cause_list_date` comes as ISO string in query params. Convert to date for PDF formatting.
        cld: date_type
        if isinstance(cause_list_date, str):
            try:
                cld = timezone.datetime.fromisoformat(cause_list_date).date()
            except Exception:
                raise ValidationError({"cause_list_date": "Invalid date format. Use YYYY-MM-DD."})
        else:
            cld = cause_list_date

        pdf_bytes = generate_cause_list_pdf_bytes(
            cause_list_date=cld,
            bench_key=str(bench_key),
            rows=rows,
        )

        filename = f"draft_cause_list_{slugify(str(bench_key))}_{cause_list_date}.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="{filename}"'
        return resp


class CauseListDraftSaveView(APIView):
    """
    Listing Officer: save a draft for date+bench_key.
    Payload should include the full accepted snapshot for the bench/date selection UI.
    """

    def post(self, request, *args, **kwargs):
        payload = CauseListDraftSaveSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        cause_list_date = payload.validated_data["cause_list_date"]
        bench_key = payload.validated_data["bench_key"]
        entries = payload.validated_data["entries"]

        user = request.user if request.user.is_authenticated else None

        with transaction.atomic():
            cause_list, created = CauseList.objects.get_or_create(
                cause_list_date=cause_list_date,
                bench_key=bench_key,
                defaults={
                    "status": CauseList.CauseListStatus.DRAFT,
                    "generated_by": user,
                },
            )

            # If it existed but was published, move back to draft for editing.
            if cause_list.status != CauseList.CauseListStatus.DRAFT:
                cause_list.status = CauseList.CauseListStatus.DRAFT
                cause_list.published_at = None
                cause_list.pdf_file = cause_list.pdf_file  # keep file; publish will overwrite later
                cause_list.save(update_fields=["status", "published_at"])

            incoming_efiling_ids = [e["efiling_id"] for e in entries]
            incoming_id_set = set(incoming_efiling_ids)

            # Upsert included state for provided entries.
            for e in entries:
                efiling_id = e["efiling_id"]
                included = bool(e.get("included", True))
                serial_no = e.get("serial_no", None)

                filing = Efiling.objects.filter(pk=efiling_id).first()
                if not filing:
                    raise ValidationError({"efiling_id": f"Invalid efiling_id={efiling_id}"})
                if filing.is_draft or filing.status != "ACCEPTED":
                    raise ValidationError(
                        {
                            "efiling_id": f"efiling_id={efiling_id} is not ACCEPTED and cannot be added to cause list."
                        }
                    )
                # We trust bench_key mapping per plan: Efiling.bench decides bench.
                if filing.bench != bench_key:
                    raise ValidationError({"bench_key": "efiling_id does not belong to selected bench_key."})

                CauseListEntry.objects.update_or_create(
                    cause_list=cause_list,
                    efiling=filing,
                    defaults={"included": included, "serial_no": serial_no},
                )

            # For a consistent snapshot UI, any missing case becomes un-included.
            # This must run even when `entries` is empty (unselect-all), so stale
            # included entries don't survive in the saved draft.
            (
                CauseListEntry.objects.filter(cause_list=cause_list)
                .exclude(efiling_id__in=incoming_id_set)
                .update(included=False, serial_no=None)
            )

        return Response(
            {"cause_list_id": cause_list.id, "status": cause_list.status},
            status=drf_status.HTTP_200_OK,
        )


class CauseListPublishView(APIView):
    """
    Listing Officer: publish a draft (generate PDF and mark PUBLISHED).
    """

    def post(self, request, pk: int, *args, **kwargs):
        cause_list = get_object_or_404(CauseList, pk=pk)

        if cause_list.status != CauseList.CauseListStatus.DRAFT:
            raise ValidationError({"detail": "Only DRAFT cause lists can be published."})

        with transaction.atomic():
            entries_qs = (
                CauseListEntry.objects.filter(cause_list=cause_list, included=True)
                .select_related("efiling")
                .all()
            )

            entries = list(entries_qs)
            # Sort by serial_no (nulls last), then by id for stability.
            included_ids = {e.efiling_id for e in entries}
            allowed_ids = _judge_approved_efiling_ids(
                cause_list.cause_list_date.isoformat(), cause_list.bench_key
            )
            if not included_ids.issubset(allowed_ids):
                raise ValidationError({"detail": "Some selected cases are not judge-approved for this date/bench."})
            entries.sort(key=lambda e: (e.serial_no is None, e.serial_no or 10**12, e.id))

            rows: List[CauseListRow] = []
            sequential_fallback = 1
            for e in entries:
                serial = e.serial_no if e.serial_no is not None else sequential_fallback
                sequential_fallback += 1
                main_parties = _main_parties_for_filing(e.efiling)
                pet_adv, resp_adv = _advocates_for_filing(e.efiling)
                rows.append(
                    CauseListRow(
                        serial_no=int(serial),
                        case_number=e.efiling.case_number or "",
                        main_parties=main_parties,
                        petitioner_advocates=pet_adv,
                        respondent_advocates=resp_adv,
                    )
                )

            pdf_bytes = generate_cause_list_pdf_bytes(
                cause_list_date=cause_list.cause_list_date,
                bench_key=cause_list.bench_key,
                rows=rows,
            )

            filename = f"cause_list_{slugify(cause_list.bench_key)}_{cause_list.cause_list_date.isoformat()}.pdf"
            cause_list.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
            cause_list.status = CauseList.CauseListStatus.PUBLISHED
            cause_list.published_at = timezone.now()
            if request.user.is_authenticated:
                cause_list.generated_by = request.user
            cause_list.save(
                update_fields=["pdf_file", "status", "published_at", "generated_by", "updated_at"]
            )

        return Response(
            {
                "id": cause_list.id,
                "status": cause_list.status,
                "pdf_url": (
                    request.build_absolute_uri(cause_list.pdf_file.url)
                    if cause_list.pdf_file and getattr(cause_list.pdf_file, "url", None)
                    else None
                ),
            },
            status=drf_status.HTTP_200_OK,
        )


class CauseListPublishDirectView(APIView):
    """
    Listing Officer: publish in one step (no explicit draft step in UI).
    Accepts (cause_list_date, bench_key, entries[]) and publishes immediately.
    """

    def post(self, request, *args, **kwargs):
        payload = CauseListPublishSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        cause_list_date = payload.validated_data["cause_list_date"]
        bench_key = payload.validated_data["bench_key"]
        entries = payload.validated_data["entries"]
        user = request.user if request.user.is_authenticated else None

        with transaction.atomic():
            cause_list, _created = CauseList.objects.get_or_create(
                cause_list_date=cause_list_date,
                bench_key=bench_key,
                defaults={
                    "status": CauseList.CauseListStatus.DRAFT,
                    "generated_by": user,
                },
            )

            # If already published, allow re-publish by regenerating PDF.
            if cause_list.status != CauseList.CauseListStatus.DRAFT:
                cause_list.status = CauseList.CauseListStatus.DRAFT
                cause_list.published_at = None
                cause_list.save(update_fields=["status", "published_at"])

            # Upsert entries (same validation as draft save)
            incoming_id_set = set()
            for e in entries:
                efiling_id = e["efiling_id"]
                included = bool(e.get("included", True))
                serial_no = e.get("serial_no", None)
                incoming_id_set.add(efiling_id)

                filing = Efiling.objects.filter(pk=efiling_id).first()
                if not filing:
                    raise ValidationError({"efiling_id": f"Invalid efiling_id={efiling_id}"})
                if filing.is_draft or filing.status != "ACCEPTED":
                    raise ValidationError({"efiling_id": f"efiling_id={efiling_id} is not ACCEPTED."})
                if filing.bench != bench_key:
                    raise ValidationError({"bench_key": "efiling_id does not belong to selected bench_key."})

                CauseListEntry.objects.update_or_create(
                    cause_list=cause_list,
                    efiling=filing,
                    defaults={"included": included, "serial_no": serial_no},
                )

            (
                CauseListEntry.objects.filter(cause_list=cause_list)
                .exclude(efiling_id__in=incoming_id_set)
                .update(included=False, serial_no=None)
            )

            included_count = CauseListEntry.objects.filter(cause_list=cause_list, included=True).count()
            if included_count == 0:
                raise ValidationError({"detail": "No cases selected for publishing."})

            included_ids = set(
                CauseListEntry.objects.filter(cause_list=cause_list, included=True).values_list(
                    "efiling_id", flat=True
                )
            )
            allowed_ids = _judge_approved_efiling_ids(
                cause_list_date.isoformat(), bench_key
            )
            if not included_ids.issubset(allowed_ids):
                raise ValidationError({"detail": "Some included cases are not judge-approved for this date/bench."})

            # Safety net: for this date, keep each case in only one bench.
            if incoming_id_set:
                other_entries = CauseListEntry.objects.filter(
                    efiling_id__in=list(incoming_id_set),
                    cause_list__cause_list_date=cause_list_date,
                ).exclude(cause_list=cause_list)
                other_cause_list_ids = list(other_entries.values_list("cause_list_id", flat=True).distinct())
                other_entries.delete()
                if other_cause_list_ids:
                    CauseList.objects.filter(
                        id__in=other_cause_list_ids,
                        status=CauseList.CauseListStatus.PUBLISHED,
                    ).update(status=CauseList.CauseListStatus.DRAFT, published_at=None)

            # Now publish (reuse publish logic inline)
            entries_qs = (
                CauseListEntry.objects.filter(cause_list=cause_list, included=True)
                .select_related("efiling")
                .all()
            )
            entries_list = list(entries_qs)
            entries_list.sort(key=lambda e: (e.serial_no is None, e.serial_no or 10**12, e.id))

            rows: List[CauseListRow] = []
            fallback = 1
            for e in entries_list:
                serial = e.serial_no if e.serial_no is not None else fallback
                fallback += 1
                main_parties = _main_parties_for_filing(e.efiling)
                pet_adv, resp_adv = _advocates_for_filing(e.efiling)
                rows.append(
                    CauseListRow(
                        serial_no=int(serial),
                        case_number=e.efiling.case_number or "",
                        main_parties=main_parties,
                        petitioner_advocates=pet_adv,
                        respondent_advocates=resp_adv,
                    )
                )

            pdf_bytes = generate_cause_list_pdf_bytes(
                cause_list_date=cause_list.cause_list_date,
                bench_key=cause_list.bench_key,
                rows=rows,
            )

            filename = f"cause_list_{slugify(cause_list.bench_key)}_{cause_list.cause_list_date.isoformat()}.pdf"
            cause_list.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
            cause_list.status = CauseList.CauseListStatus.PUBLISHED
            cause_list.published_at = timezone.now()
            if user:
                cause_list.generated_by = user
            cause_list.save(update_fields=["pdf_file", "status", "published_at", "generated_by", "updated_at"])

        return Response(
            {
                "id": cause_list.id,
                "status": cause_list.status,
                "pdf_url": (
                    request.build_absolute_uri(cause_list.pdf_file.url)
                    if cause_list.pdf_file and getattr(cause_list.pdf_file, "url", None)
                    else None
                ),
            },
            status=drf_status.HTTP_200_OK,
        )


class PublishedCauseListByDateView(APIView):
    def get(self, request, *args, **kwargs):
        cause_list_date = request.query_params.get("cause_list_date")
        if not cause_list_date:
            raise ValidationError({"detail": "cause_list_date is required."})

        lists = (
            CauseList.objects.filter(
                cause_list_date=cause_list_date,
                status=CauseList.CauseListStatus.PUBLISHED,
            )
            .order_by("bench_key")
            .all()
        )

        response_items = []
        for cl in lists:
            response_items.append(
                {
                    "id": cl.id,
                    "bench_key": cl.bench_key,
                    "pdf_url": (
                        request.build_absolute_uri(cl.pdf_file.url)
                        if cl.pdf_file and getattr(cl.pdf_file, "url", None)
                        else None
                    ),
                }
            )

        return Response({"items": response_items}, status=drf_status.HTTP_200_OK)


class LatestPublishedCauseListsView(APIView):
    """
    Advocate/any: returns the latest published cause list date and bench pdfs.
    """

    def get(self, request, *args, **kwargs):
        latest = (
            CauseList.objects.filter(status=CauseList.CauseListStatus.PUBLISHED)
            .order_by("-cause_list_date", "-published_at", "-id")
            .first()
        )
        if not latest:
            return Response({"found": False, "cause_list_date": None, "items": []}, status=drf_status.HTTP_200_OK)

        cause_list_date = latest.cause_list_date
        lists = (
            CauseList.objects.filter(
                cause_list_date=cause_list_date,
                status=CauseList.CauseListStatus.PUBLISHED,
            )
            .order_by("bench_key")
            .all()
        )

        items = []
        for cl in lists:
            items.append(
                {
                    "id": cl.id,
                    "bench_key": cl.bench_key,
                    "pdf_url": (
                        request.build_absolute_uri(cl.pdf_file.url)
                        if cl.pdf_file and getattr(cl.pdf_file, "url", None)
                        else None
                    ),
                }
            )

        return Response(
            {"found": True, "cause_list_date": str(cause_list_date), "items": items},
            status=drf_status.HTTP_200_OK,
        )


class LatestPublishedCauseListLookupView(APIView):
    """
    Bulk lookup cases in the latest published cause list.
    Input: { case_numbers: [...] }
    Output: { found: bool, cause_list_date, matches: {<case_number>: {bench_key, serial_no, pdf_url}} }
    """

    def post(self, request, *args, **kwargs):
        payload = LatestCauseListLookupSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        case_numbers = [str(x).strip() for x in payload.validated_data.get("case_numbers", []) if str(x).strip()]
        case_numbers = list(dict.fromkeys(case_numbers))  # de-dupe, keep order

        latest = (
            CauseList.objects.filter(status=CauseList.CauseListStatus.PUBLISHED)
            .order_by("-cause_list_date", "-published_at", "-id")
            .first()
        )
        if not latest or not case_numbers:
            return Response(
                {"found": False, "cause_list_date": None if not latest else str(latest.cause_list_date), "matches": {}},
                status=drf_status.HTTP_200_OK,
            )

        cause_list_date = latest.cause_list_date

        entries = (
            CauseListEntry.objects.filter(
                included=True,
                efiling__case_number__in=case_numbers,
                cause_list__cause_list_date=cause_list_date,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
            )
            .select_related("cause_list", "efiling")
            .order_by("-cause_list__published_at", "-id")
        )

        matches = {}
        for e in entries:
            cn = e.efiling.case_number
            if not cn or cn in matches:
                continue
            cl = e.cause_list
            matches[cn] = {
                "bench_key": cl.bench_key,
                "serial_no": e.serial_no,
                "pdf_url": (
                    request.build_absolute_uri(cl.pdf_file.url)
                    if cl.pdf_file and getattr(cl.pdf_file, "url", None)
                    else None
                ),
            }

        return Response(
            {"found": True, "cause_list_date": str(cause_list_date), "matches": matches},
            status=drf_status.HTTP_200_OK,
        )


class NextPublishedCauseListLookupView(APIView):
    """
    Advocate: for each case_number, return the nearest upcoming published cause list (>= today).
    Input: { case_numbers: [...] }
    Output: { matches: {case_number: {cause_list_date, bench_key, serial_no, pdf_url}} }
    """

    def post(self, request, *args, **kwargs):
        payload = NextCauseListLookupSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        case_numbers = [str(x).strip() for x in payload.validated_data.get("case_numbers", []) if str(x).strip()]
        case_numbers = list(dict.fromkeys(case_numbers))
        if not case_numbers:
            return Response({"matches": {}}, status=drf_status.HTTP_200_OK)

        today = timezone.localdate()
        qs = (
            CauseListEntry.objects.filter(
                included=True,
                efiling__case_number__in=case_numbers,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
                cause_list__cause_list_date__gte=today,
            )
            .select_related("cause_list", "efiling")
            .order_by("cause_list__cause_list_date", "-cause_list__published_at", "-id")
        )

        matches = {}
        for e in qs:
            cn = e.efiling.case_number
            if not cn or cn in matches:
                continue
            cl = e.cause_list
            matches[cn] = {
                "cause_list_date": str(cl.cause_list_date),
                "bench_key": cl.bench_key,
                "serial_no": e.serial_no,
                "pdf_url": (
                    request.build_absolute_uri(cl.pdf_file.url)
                    if cl.pdf_file and getattr(cl.pdf_file, "url", None)
                    else None
                ),
            }

        return Response({"matches": matches}, status=drf_status.HTTP_200_OK)


class CauseListEntryLookupByCaseNumberView(APIView):
    def get(self, request, *args, **kwargs):
        cause_list_date = request.query_params.get("cause_list_date")
        case_number = request.query_params.get("case_number")

        if not cause_list_date or not case_number:
            raise ValidationError({"detail": "cause_list_date and case_number are required."})

        filing = Efiling.objects.filter(case_number=case_number).first()
        if not filing:
            return Response({"found": False}, status=drf_status.HTTP_200_OK)

        entry = (
            CauseListEntry.objects.filter(
                efiling=filing,
                included=True,
                cause_list__cause_list_date=cause_list_date,
                cause_list__status=CauseList.CauseListStatus.PUBLISHED,
            )
            .select_related("cause_list")
            .order_by("-cause_list__published_at", "-id")
            .first()
        )

        if not entry:
            return Response({"found": False}, status=drf_status.HTTP_200_OK)

        cl = entry.cause_list
        return Response(
            {
                "found": True,
                "cause_list_id": cl.id,
                "bench_key": cl.bench_key,
                "serial_no": entry.serial_no,
                "pdf_url": (
                    request.build_absolute_uri(cl.pdf_file.url)
                    if cl.pdf_file and getattr(cl.pdf_file, "url", None)
                    else None
                ),
            },
            status=drf_status.HTTP_200_OK,
        )


class RegisteredCasesListView(APIView):
    """
    Listing Officer: show only scrutiny-completed (registered) cases.
    Filter rule per requirement: Efiling.is_draft=false AND Efiling.status='ACCEPTED'
    """

    def get(self, request, *args, **kwargs):
        page_size_raw = request.query_params.get("page_size")
        page_size = int(page_size_raw) if page_size_raw not in (None, "", "null") else 50

        qs = Efiling.objects.filter(is_draft=False, status="ACCEPTED").order_by("-id")
        total = qs.count()

        # Prefetch parties and case details to avoid N+1 for UI rendering.
        case_details_qs = EfilingCaseDetails.objects.select_related("dispute_state", "dispute_district").order_by(
            "id"
        )

        qs = qs.prefetch_related(
            Prefetch("litigants"),
            Prefetch("case_details", queryset=case_details_qs),
        )

        efilings = list(qs[:page_size])
        efiling_ids = [e.id for e in efilings]

        items = []
        for e in efilings:
            respondent = next((l for l in e.litigants.all() if not getattr(l, "is_petitioner", False)), None)
            case_detail = e.case_details.all().first() if hasattr(e, "case_details") else None

            items.append(
                {
                    "efiling_id": e.id,
                    "case_number": e.case_number,
                    "e_filing_number": e.e_filing_number,
                    "bench": e.bench,
                    "petitioner_name": e.petitioner_name,
                    "respondent_name": getattr(respondent, "name", None) if respondent else None,
                    "cause_of_action": getattr(case_detail, "cause_of_action", None) if case_detail else None,
                    "date_of_cause_of_action": getattr(case_detail, "date_of_cause_of_action", None).isoformat()
                    if getattr(case_detail, "date_of_cause_of_action", None)
                    else None,
                    "dispute_state": getattr(getattr(case_detail, "dispute_state", None), "state", None)
                    if case_detail
                    else None,
                    "dispute_district": getattr(getattr(case_detail, "dispute_district", None), "district", None)
                    if case_detail
                    else None,
                    "dispute_taluka": getattr(case_detail, "dispute_taluka", None) if case_detail else None,
                    "accepted_at": e.accepted_at.isoformat() if getattr(e, "accepted_at", None) else None,
                }
            )

        return Response({"total": total, "items": items}, status=drf_status.HTTP_200_OK)


class AssignBenchesView(APIView):
    """
    Listing Officer: bulk-assign benches for registered cases.
    Updates `Efiling.bench` directly so cause-list generation works unchanged.
    """

    def post(self, request, *args, **kwargs):
        payload = AssignBenchesSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        assignments = payload.validated_data["assignments"]
        if not assignments:
            return Response({"updated": 0}, status=drf_status.HTTP_200_OK)

        # Deduplicate by efiling_id, keep last selection.
        assign_map: dict[int, str] = {}
        for a in assignments:
            assign_map[int(a["efiling_id"])] = a["bench_key"]

        efiling_ids = list(assign_map.keys())
        ef_qs = Efiling.objects.filter(id__in=efiling_ids, is_draft=False, status="ACCEPTED").all()
        ef_by_id = {e.id: e for e in ef_qs}

        missing = sorted([eid for eid in efiling_ids if eid not in ef_by_id])
        if missing:
            raise ValidationError({"efiling_id": f"Not found or not ACCEPTED: {missing}"})

        updated_instances = []
        for eid, bench_key in assign_map.items():
            e = ef_by_id[eid]
            e.bench = bench_key
            updated_instances.append(e)

        Efiling.objects.bulk_update(updated_instances, ["bench"])

        # Enforce "one case -> one bench" for the latest published cause list date only.
        latest = (
            CauseList.objects.filter(status=CauseList.CauseListStatus.PUBLISHED)
            .order_by("-cause_list_date", "-published_at", "-id")
            .first()
        )
        if latest:
            latest_date = latest.cause_list_date
            moved_case_ids = list(assign_map.keys())

            # Remove entries for these cases from any other bench on the latest date.
            other_q = Q()
            for eid in moved_case_ids:
                other_q |= Q(efiling_id=eid) & ~Q(cause_list__bench_key=assign_map[eid])

            other_entries = CauseListEntry.objects.filter(
                other_q,
                cause_list__cause_list_date=latest_date,
            )

            affected_cause_list_ids = list(other_entries.values_list("cause_list_id", flat=True).distinct())
            other_entries.delete()

            if affected_cause_list_ids:
                CauseList.objects.filter(id__in=affected_cause_list_ids).update(
                    status=CauseList.CauseListStatus.DRAFT,
                    published_at=None,
                )

        return Response({"updated": len(updated_instances)}, status=drf_status.HTTP_200_OK)

        if not entry:
            return Response({"found": False}, status=drf_status.HTTP_200_OK)

        cl = entry.cause_list
        return Response(
            {
                "found": True,
                "cause_list_id": cl.id,
                "bench_key": cl.bench_key,
                "serial_no": entry.serial_no,
                "pdf_url": cl.pdf_file.url if cl.pdf_file else None,
            },
            status=drf_status.HTTP_200_OK,
        )

