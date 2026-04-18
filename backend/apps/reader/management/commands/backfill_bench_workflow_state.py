from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.judge.models import CourtroomJudgeDecision
from apps.listing.models import CauseList
from apps.reader.models import CourtroomForward
from apps.reader.workflow_state import (
    apply_cause_list_published,
    apply_judge_decision,
    apply_reader_assign_date,
    upsert_state_on_forward,
)


class Command(BaseCommand):
    help = "Backfill canonical BenchWorkflowState from legacy workflow tables."

    def handle(self, *args, **options):
        forwards = CourtroomForward.objects.order_by("id").all()
        f_count = 0
        for f in forwards:
            upsert_state_on_forward(
                efiling_id=int(f.efiling_id),
                forwarded_for_date=f.forwarded_for_date,
                bench_key=str(f.bench_key),
                forwarded_by=f.forwarded_by,
            )
            f_count += 1

        d_count = 0
        for d in CourtroomJudgeDecision.objects.order_by("id").all():
            forward = (
                CourtroomForward.objects.filter(
                    efiling_id=d.efiling_id,
                    forwarded_for_date=d.forwarded_for_date,
                )
                .order_by("-id")
                .first()
            )
            if not forward or not d.bench_role_group:
                continue
            apply_judge_decision(
                efiling_id=int(d.efiling_id),
                forwarded_for_date=d.forwarded_for_date,
                bench_key=str(forward.bench_key),
                bench_role_group=str(d.bench_role_group),
                judge_user_id=int(d.judge_user_id),
                status=str(d.status or ""),
                approved=bool(d.approved),
                decision_notes=d.decision_notes,
            )
            if d.listing_date:
                apply_reader_assign_date(
                    efiling_ids=[int(d.efiling_id)],
                    forwarded_for_date=d.forwarded_for_date,
                    listing_date=d.listing_date,
                    listing_remark=d.reader_listing_remark,
                    assigned_by=d.updated_by,
                    bench_key=str(forward.bench_key),
                )
            d_count += 1

        p_count = 0
        for cl in CauseList.objects.filter(status=CauseList.CauseListStatus.PUBLISHED).all():
            p_count += apply_cause_list_published(cl)

        self.stdout.write(
            self.style.SUCCESS(
                f"Backfill complete. forwards={f_count} decisions={d_count} published_updates={p_count}"
            )
        )
