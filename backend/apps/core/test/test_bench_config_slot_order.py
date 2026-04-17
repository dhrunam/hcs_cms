"""Bench slot order (BENCH_S0…) follows bench_t row id, not judge seniority alone."""

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.core.bench_config import get_bench_configuration
from apps.core.models import BenchT, JudgeT


class BenchConfigSlotOrderTest(TestCase):
    def test_slots_follow_bench_t_row_order_not_seniority(self):
        """
        If puisne Judge 2 has numerically lower seniority than puisne Judge 1, seniority-only
        ordering used to seat Judge 2 in BENCH_S1 and could drop Judge 1 from the active
        composition when MAX_BENCH_JUDGES truncates — misrouting forwards.
        """
        today = timezone.localdate()
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")

        def judge_user(prefix: str) -> User:
            u = User.objects.create_user(
                email=f"{prefix}@slot-order.test",
                username=prefix,
                password="x",
            )
            u.groups.add(grp_j)
            return u

        u_cj = judge_user("cj")
        u_j1 = judge_user("j1")
        u_j2 = judge_user("j2")

        j_cj = JudgeT.objects.create(
            user=u_cj,
            judge_code="SO-CJ",
            judge_name="Chief Justice",
            seniority=1,
            date_of_joining=today,
        )
        j_j1 = JudgeT.objects.create(
            user=u_j1,
            judge_code="SO-J1",
            judge_name="Hon Judge 1",
            seniority=100,
            date_of_joining=today,
        )
        j_j2 = JudgeT.objects.create(
            user=u_j2,
            judge_code="SO-J2",
            judge_name="Hon Judge 2",
            seniority=5,
            date_of_joining=today,
        )

        code = "DBX"
        # Roster order: CJ, puisne 1, puisne 2 (row ids increase in this order).
        BenchT.objects.create(
            bench_code=code,
            bench_name="Division",
            bench_type_code="DB",
            judge_code=j_cj.judge_code,
            judge=j_cj,
            from_date=today,
        )
        BenchT.objects.create(
            bench_code=code,
            bench_name="Division",
            bench_type_code="DB",
            judge_code=j_j1.judge_code,
            judge=j_j1,
            from_date=today,
        )
        BenchT.objects.create(
            bench_code=code,
            bench_name="Division",
            bench_type_code="DB",
            judge_code=j_j2.judge_code,
            judge=j_j2,
            from_date=today,
        )

        cfg = get_bench_configuration(code)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.judge_user_ids, (u_cj.id, u_j1.id, u_j2.id))
        self.assertEqual(cfg.judge_groups[0], "BENCH_S0")
        self.assertEqual(cfg.judge_groups[1], "BENCH_S1")
        self.assertEqual(cfg.judge_groups[2], "BENCH_S2")
