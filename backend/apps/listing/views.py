from __future__ import annotations

from typing import Any, Dict, List, Set

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

from apps.core.bench_config import bench_key_aliases_for_seated_judge
from apps.core.models import (
    Efiling,
    EfilerDocumentAccess,
    EfilingCaseDetails,
    EfilingLitigant,
)
from apps.efiling.party_display import build_petitioner_vs_respondent
from apps.judge.models import (
    CourtroomDecisionRequestedDocument,
    CourtroomJudgeDecision,
)
from apps.reader.models import CourtroomForward
from apps.reader.workflow_state import apply_cause_list_published
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
from django.db.models import Count

def _cause_list_target_efiling_ids(cld_obj: date_type | None, bench_key: str) -> Set[int]:
    """
    Cases available for this cause list calendar day:
    only those explicitly assigned by Reader via listing_date for the same bench.
    """
    if not cld_obj:
        return set()
    on_bench = set(
        CourtroomForward.objects.filter(bench_key=bench_key).values_list(
            "efiling_id", flat=True
        )
    )
    by_listing = set(
        CourtroomJudgeDecision.objects.filter(
            listing_date=cld_obj,
            efiling_id__in=on_bench,
            # Include only files explicitly pushed by reader into listing flow.
            reader_listing_remark__isnull=False,
        ).values_list("efiling_id", flat=True)
    )
    return set(by_listing)


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
        cause_list_type = (
            draft.cause_list_type if draft else CauseList.CauseListType.DAILY
        )

        # Auto preselect all accepted filings for this bench_key.
        approved_only_raw = request.query_params.get("approved_only", "true")
        approved_only = approved_only_raw.strip().lower() in {"true", "1", "yes", "y"}

        judge_listing_date_map: Dict[int, str | None] = {}
        judge_listing_remark_map: Dict[int, str | None] = {}
        forwarded_for_date_map: Dict[int, str | None] = {}
        if approved_only:
            # WORKFLOW CORRECTION: Use Reader's 'Forward' as the signal for the Listing Officer.
            try:
                cld_obj = timezone.datetime.fromisoformat(cause_list_date).date()
            except ValueError:
                cld_obj = None

            target_ids = _cause_list_target_efiling_ids(cld_obj, bench_key)
            if target_ids:
                forward_rows = (
                    CourtroomForward.objects.filter(
                        efiling_id__in=target_ids,
                        bench_key=bench_key,
                    )
                    .values("efiling_id", "forwarded_for_date")
                    .order_by("efiling_id", "-forwarded_for_date", "-id")
                )
                for row in forward_rows:
                    eid = int(row["efiling_id"])
                    if eid not in forwarded_for_date_map:
                        d = row.get("forwarded_for_date")
                        forwarded_for_date_map[eid] = d.isoformat() if d else None

            # Still pull Judge data (if any) as metadata for the Listing Officer.
            if target_ids:
                rows = (
                    CourtroomJudgeDecision.objects.filter(
                        efiling_id__in=target_ids,
                        # We don't filter by approved=True here because we want to see 
                        # all suggested metadata for forwarded cases.
                    )
                    .values("efiling_id", "listing_date", "reader_listing_remark")
                    .order_by("efiling_id", "-listing_date", "-id")
                )
                for row in rows:
                    eid = int(row["efiling_id"])
                    if eid not in judge_listing_date_map:
                        d = row.get("listing_date")
                        judge_listing_date_map[eid] = d.isoformat() if d else None
                        judge_listing_remark_map[eid] = row.get("reader_listing_remark")
            accepted = (
                Efiling.objects.filter(
                    id__in=target_ids,
                    is_draft=False,
                    status="ACCEPTED",
                )
                .prefetch_related("litigants")
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
                .prefetch_related("litigants")
                .order_by("id")
                .all()
            )

        existing_entries = {}
        if draft:
            qs = CauseListEntry.objects.filter(cause_list=draft).only(
                "efiling_id", "included", "serial_no", "petitioner_advocate", "respondent_advocate", "selected_ias"
            )
            existing_entries = {row.efiling_id: row for row in qs}

        # Fetch all IAs for these filings
        from apps.core.models import IA
        efiling_ids = [f.id for f in accepted]
        all_ias = IA.objects.filter(e_filing_id__in=efiling_ids).values("e_filing_id", "ia_number", "ia_text")
        ia_map: Dict[int, List[Dict[str, str]]] = {}
        for ia in all_ias:
            eid = int(ia["e_filing_id"])
            if eid not in ia_map:
                ia_map[eid] = []
            ia_map[eid].append({"ia_number": ia["ia_number"], "ia_text": ia["ia_text"]})

        items: List[Dict[str, Any]] = []
        for idx, filing in enumerate(accepted, start=1):
            existing = existing_entries.get(filing.id)
            if existing is not None:
                included = bool(existing.included)
                serial_no = (
                    existing.serial_no if existing.serial_no is not None else idx
                )
                petitioner_advocate = existing.petitioner_advocate or ""
                respondent_advocate = existing.respondent_advocate or ""
                selected_ias = existing.selected_ias or []
            else:
                # WORKFLOW IMPROVEMENT: Default to 'True' for forwarded cases 
                # to reduce manual work for the Listing Officer.
                included = True
                serial_no = idx
                petitioner_advocate = ""
                respondent_advocate = ""
                selected_ias = []

            items.append(
                {
                    "efiling_id": filing.id,
                    "e_filing_number": filing.e_filing_number,
                    "case_number": filing.case_number,
                    "petitioner_name": filing.petitioner_name,
                    "petitioner_vs_respondent": (filing.petitioner_name or "").strip() or build_petitioner_vs_respondent(
                        filing, fallback_petitioner_name=filing.petitioner_name or ""
                    ),
                    "included": included,
                    "serial_no": serial_no,
                    "petitioner_advocate": petitioner_advocate,
                    "respondent_advocate": respondent_advocate,
                    "available_ias": ia_map.get(filing.id, []),
                    "selected_ias": selected_ias,
                    "forwarded_for_date": forwarded_for_date_map.get(filing.id),
                    "judge_listing_date": judge_listing_date_map.get(filing.id),
                    "reader_listing_remark": judge_listing_remark_map.get(filing.id),
                }
            )

        return Response(
            {
                "cause_list_id": draft.id if draft else None,
                "cause_list_date": cause_list_date,
                "bench_key": bench_key,
                "cause_list_type": cause_list_type,
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
        cause_list_type = (
            draft.cause_list_type if draft else CauseList.CauseListType.DAILY
        )

        try:
            cld_obj = timezone.datetime.fromisoformat(cause_list_date).date()
        except ValueError:
            cld_obj = None

        target_ids = _cause_list_target_efiling_ids(cld_obj, bench_key)

        accepted = (
            Efiling.objects.filter(id__in=target_ids, is_draft=False, status="ACCEPTED")
            .order_by("id")
            .all()
        )

        existing_entries: dict[int, CauseListEntry] = {}
        if draft:
            qs = (
                CauseListEntry.objects.filter(cause_list=draft)
                .only("efiling_id", "included", "serial_no", "petitioner_advocate", "respondent_advocate", "selected_ias")
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
            
            # Formatted IA strings
            ia_list = existing.selected_ias if existing and existing.selected_ias else []
            ia_items = []
            for ia_obj in ia_list:
                num = ia_obj.get("ia_number", "")
                txt = ia_obj.get("ia_text", "")
                ia_items.append(f"(with) IA {num} ({txt})")
            ia_str = "\n".join(ia_items)

            # Advocates: manual or auto
            pet_adv_auto, resp_adv_auto = _advocates_for_filing(filing)
            if existing:
                pet_adv = (existing.petitioner_advocate or "").strip() or pet_adv_auto
                resp_adv = (existing.respondent_advocate or "").strip() or resp_adv_auto
            else:
                pet_adv, resp_adv = pet_adv_auto, resp_adv_auto

            rows.append(
                CauseListRow(
                    serial_no=int(serial),
                    case_number=filing.case_number or "-",
                    ia_info=ia_str,
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
            cause_list_type=cause_list_type,
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
        if not payload.is_valid():
            raise ValidationError(payload.errors)

        cause_list_date = payload.validated_data["cause_list_date"]
        bench_key = payload.validated_data["bench_key"]
        cause_list_type = payload.validated_data.get("cause_list_type") or CauseList.CauseListType.DAILY
        entries = payload.validated_data["entries"]

        user = request.user if request.user.is_authenticated else None
        updated_at = timezone.now()

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
            if cause_list.cause_list_type != cause_list_type:
                cause_list.cause_list_type = cause_list_type
                cause_list.save(update_fields=["cause_list_type", "updated_at"])

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

                CauseListEntry.objects.update_or_create(
                    cause_list=cause_list,
                    efiling=filing,
                    defaults={
                        "included": included,
                        "serial_no": serial_no,
                        "petitioner_advocate": e.get("petitioner_advocate", ""),
                        "respondent_advocate": e.get("respondent_advocate", ""),
                        "selected_ias": e.get("selected_ias", []),
                    },
                )

            # For a consistent snapshot UI, any missing case becomes un-included.
            # This must run even when `entries` is empty (unselect-all), so stale
            # included entries don't survive in the saved draft.
            (
                CauseListEntry.objects.filter(cause_list=cause_list)
                .exclude(efiling_id__in=incoming_id_set)
                .update(included=False, serial_no=None, updated_by=user, updated_at=updated_at)
            )

        return Response(
            {"cause_list_id": cause_list.id, "status": cause_list.status, "cause_list_type": cause_list.cause_list_type},
            status=drf_status.HTTP_200_OK,
        )


class CauseListPublishView(APIView):
    """
    Listing Officer: publish a draft (generate PDF and mark PUBLISHED).
    """

    def post(self, request, pk: int, *args, **kwargs):
        cause_list = get_object_or_404(CauseList, pk=pk)

        if cause_list.status != CauseList.CauseListStatus.DRAFT:
            print(f"DEBUG: CauseListPublishView error: status is {cause_list.status}, not DRAFT.")
            raise ValidationError({"detail": "Only DRAFT cause lists can be published."})

        with transaction.atomic():
            entries_qs = (
                CauseListEntry.objects.filter(cause_list=cause_list, included=True)
                .select_related("efiling")
                .all()
            )

            entries = list(entries_qs)
            included_ids = {e.efiling_id for e in entries}
            # Sort by serial_no (nulls last), then by id for stability.
            # WORKFLOW CORRECTION: Listing Officer's publication is final. 
            # It only requires that the cases were forwarded by the Reader for this date.
            try:
                cld_str = cause_list.cause_list_date.isoformat()
                cld_obj = cause_list.cause_list_date
            except:
                raise ValidationError({"detail": "Invalid cause list date."})

            allowed_ids = _cause_list_target_efiling_ids(cld_obj, cause_list.bench_key)

            if not included_ids.issubset(allowed_ids):
                raise ValidationError(
                    {
                        "detail": "Some selected cases are not on reader forward/listing workflow for this cause list date and bench."
                    }
                )
            entries.sort(key=lambda e: (e.serial_no is None, e.serial_no or 10**12, e.id))

            rows: List[CauseListRow] = []
            sequential_fallback = 1
            for e in entries:
                serial = e.serial_no if e.serial_no is not None else sequential_fallback
                sequential_fallback += 1
                main_parties = _main_parties_for_filing(e.efiling)
                
                # Use manually entered advocates if present, otherwise fallback to auto-generated
                pet_adv_auto, resp_adv_auto = _advocates_for_filing(e.efiling)
                pet_adv = (e.petitioner_advocate or "").strip() or pet_adv_auto
                resp_adv = (e.respondent_advocate or "").strip() or resp_adv_auto
                
                # IAs
                ia_list = e.selected_ias or []
                ia_items = []
                for ia_obj in ia_list:
                    num = ia_obj.get("ia_number", "")
                    txt = ia_obj.get("ia_text", "")
                    ia_items.append(f"(with) IA {num} ({txt})")
                ia_str = "\n".join(ia_items)

                rows.append(
                    CauseListRow(
                        serial_no=int(serial),
                        case_number=e.efiling.case_number or "-",
                        ia_info=ia_str,
                        main_parties=main_parties,
                        petitioner_advocates=pet_adv,
                        respondent_advocates=resp_adv,
                    )
                )

            pdf_bytes = generate_cause_list_pdf_bytes(
                cause_list_date=cause_list.cause_list_date,
                bench_key=cause_list.bench_key,
                cause_list_type=cause_list.cause_list_type,
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
            apply_cause_list_published(cause_list)

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
        cause_list_type = payload.validated_data.get("cause_list_type") or CauseList.CauseListType.DAILY
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
            if cause_list.cause_list_type != cause_list_type:
                cause_list.cause_list_type = cause_list_type
                cause_list.save(update_fields=["cause_list_type", "updated_at"])

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

                CauseListEntry.objects.update_or_create(
                    cause_list=cause_list,
                    efiling=filing,
                    defaults={
                        "included": included, 
                        "serial_no": serial_no,
                        "petitioner_advocate": e.get("petitioner_advocate", ""),
                        "respondent_advocate": e.get("respondent_advocate", ""),
                        "selected_ias": e.get("selected_ias", []),
                    },
                )

            (
                CauseListEntry.objects.filter(cause_list=cause_list)
                .exclude(efiling_id__in=incoming_id_set)
                .update(
                    included=False,
                    serial_no=None,
                    updated_by=user,
                    updated_at=timezone.now(),
                )
            )

            included_count = CauseListEntry.objects.filter(cause_list=cause_list, included=True).count()
            if included_count == 0:
                raise ValidationError({"detail": "No cases selected for publishing."})

            included_ids = set(
                CauseListEntry.objects.filter(cause_list=cause_list, included=True).values_list(
                    "efiling_id", flat=True
                )
            )
            allowed_ids = _cause_list_target_efiling_ids(cause_list_date, bench_key)
            if not included_ids.issubset(allowed_ids):
                raise ValidationError(
                    {
                        "detail": "Some included cases are not on reader forward/listing workflow for this cause list date and bench."
                    }
                )

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
                    ).update(
                        status=CauseList.CauseListStatus.DRAFT,
                        published_at=None,
                        updated_by=user,
                        updated_at=timezone.now(),
                    )

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
                
                # Use manually entered advocates if present, otherwise fallback to auto-generated
                pet_adv_auto, resp_adv_auto = _advocates_for_filing(e.efiling)
                pet_adv = (e.petitioner_advocate or "").strip() or pet_adv_auto
                resp_adv = (e.respondent_advocate or "").strip() or resp_adv_auto

                # IAs
                ia_list = e.selected_ias or []
                ia_items = []
                for ia_obj in ia_list:
                    num = ia_obj.get("ia_number", "")
                    txt = ia_obj.get("ia_text", "")
                    ia_items.append(f"(with) IA {num} ({txt})")
                ia_str = "\n".join(ia_items)

                rows.append(
                    CauseListRow(
                        serial_no=int(serial),
                        case_number=e.efiling.case_number or "-",
                        ia_info=ia_str,
                        main_parties=main_parties,
                        petitioner_advocates=pet_adv,
                        respondent_advocates=resp_adv,
                    )
                )

            pdf_bytes = generate_cause_list_pdf_bytes(
                cause_list_date=cause_list.cause_list_date,
                bench_key=cause_list.bench_key,
                cause_list_type=cause_list.cause_list_type,
                rows=rows,
            )

            filename = f"cause_list_{slugify(cause_list.bench_key)}_{cause_list.cause_list_date.isoformat()}.pdf"
            cause_list.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
            cause_list.status = CauseList.CauseListStatus.PUBLISHED
            cause_list.published_at = timezone.now()
            if user:
                cause_list.generated_by = user
            cause_list.save(update_fields=["pdf_file", "status", "published_at", "generated_by", "updated_at"])
            apply_cause_list_published(cause_list)

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

        lists = CauseList.objects.filter(
            cause_list_date=cause_list_date,
            status=CauseList.CauseListStatus.PUBLISHED,
        )
        for_seated = (request.query_params.get("for_seated_judge") or "").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }
        if for_seated:
            if not getattr(request.user, "is_authenticated", False):
                raise ValidationError({"detail": "Authentication required when for_seated_judge is set."})
            aliases = bench_key_aliases_for_seated_judge(request.user)
            if not aliases:
                return Response({"items": []}, status=drf_status.HTTP_200_OK)
            lists = lists.filter(bench_key__in=list(aliases))

        lists = list(
            lists.annotate(
                included_count=Count("entries", filter=Q(entries__included=True)),
            )
            .order_by("bench_key", "-published_at", "-id")
            .all()
        )

        latest_by_bench: dict[str, CauseList] = {}
        for cl in lists:
            latest_by_bench.setdefault(str(cl.bench_key), cl)

        response_items = []
        for bench_key in sorted(latest_by_bench.keys()):
            cl = latest_by_bench[bench_key]
            response_items.append(
                {
                    "id": cl.id,
                    "bench_key": cl.bench_key,
                    "included_count": int(getattr(cl, "included_count", 0) or 0),
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
                "efiling_id": filing.id,
                "cause_list_id": cl.id,
                "cause_list_date": str(cl.cause_list_date),
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

