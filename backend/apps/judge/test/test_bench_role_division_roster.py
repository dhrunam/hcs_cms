"""Division benches: slot resolution from bench roster, not duplicate Django groups."""

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import BenchT, Efiling, JudgeT
from apps.judge.bench_role import resolve_bench_role_group_for_forward
from apps.judge.models import CourtroomJudgeDecision
from apps.reader.models import CourtroomForward


class DivisionBenchRosterOverridesDuplicateSlotGroupsTest(TestCase):
    """
    If both judges carry the same slot group (e.g. only BENCH_S0), role resolution
    must still use seated judge order so co-judges do not collide on one bench_role_group.
    """

    def setUp(self):
        self.fwd_date = timezone.localdate()
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        grp_s0, _ = Group.objects.get_or_create(name="BENCH_S0")

        self.judge_a = User.objects.create_user(
            email="div.a@example.com",
            username="div_a",
            password="x",
        )
        self.judge_b = User.objects.create_user(
            email="div.b@example.com",
            username="div_b",
            password="x",
        )
        # Misconfiguration: both only have BENCH_S0 (would old-code both resolve to BENCH_S0).
        for u in (self.judge_a, self.judge_b):
            u.groups.add(grp_j, grp_s0)

        self.jt_a = JudgeT.objects.create(
            user=self.judge_a,
            judge_code="DIV-A",
            judge_name="Senior",
            date_of_joining=self.fwd_date,
        )
        self.jt_b = JudgeT.objects.create(
            user=self.judge_b,
            judge_code="DIV-B",
            judge_name="Junior",
            date_of_joining=self.fwd_date,
        )
        code = "DIVX"
        BenchT.objects.create(
            bench_code=code,
            bench_name="Division",
            bench_type_code="DB",
            judge_code=self.jt_a.judge_code,
            judge=self.jt_a,
            from_date=self.fwd_date,
        )
        BenchT.objects.create(
            bench_code=code,
            bench_name="Division",
            bench_type_code="DB",
            judge_code=self.jt_b.judge_code,
            judge=self.jt_b,
            from_date=self.fwd_date,
        )

        self.filing = Efiling.objects.create(
            case_number="DIV-001",
            e_filing_number="ASK20260000001C202600301",
            bench=code,
            petitioner_name="P",
            petitioner_contact="1",
            is_draft=False,
            status="ACCEPTED",
        )
        for brg in ("BENCH_S0", "BENCH_S1"):
            CourtroomForward.objects.create(
                efiling=self.filing,
                forwarded_for_date=self.fwd_date,
                bench_key=code,
                bench_role_group=brg,
                listing_summary="S",
                forwarded_by=self.judge_a,
            )

    def test_resolve_uses_roster_not_duplicate_bench_s0_group(self):
        self.assertEqual(
            resolve_bench_role_group_for_forward(self.judge_a, "DIVX"),
            "BENCH_S0",
        )
        self.assertEqual(
            resolve_bench_role_group_for_forward(self.judge_b, "DIVX"),
            "BENCH_S1",
        )

    def test_both_judges_can_post_decisions_independently(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.judge_a)
        r1 = client_a.post(
            "/api/v1/judge/courtroom/decisions/",
            {
                "efiling_id": self.filing.id,
                "forwarded_for_date": self.fwd_date.isoformat(),
                "decision_notes": "read by A",
            },
            format="json",
        )
        self.assertEqual(r1.status_code, 200, r1.data)

        client_b = APIClient()
        client_b.force_authenticate(user=self.judge_b)
        r2 = client_b.post(
            "/api/v1/judge/courtroom/decisions/",
            {
                "efiling_id": self.filing.id,
                "forwarded_for_date": self.fwd_date.isoformat(),
                "decision_notes": "read by B",
            },
            format="json",
        )
        self.assertEqual(r2.status_code, 200, r2.data)

        rows = list(
            CourtroomJudgeDecision.objects.filter(
                efiling_id=self.filing.id,
                forwarded_for_date=self.fwd_date,
            ).order_by("bench_role_group")
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual({r.bench_role_group for r in rows}, {"BENCH_S0", "BENCH_S1"})
