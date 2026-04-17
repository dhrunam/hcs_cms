from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.core.models import BenchT, Efiling, JudgeT, ReaderJudgeAssignment
from apps.judge.models import CourtroomJudgeDecision
from apps.judge.models import JudgeStenoMapping
from apps.listing.models import CauseList, CauseListEntry
from apps.reader.models import (
    BenchWorkflowState,
    CourtroomForward,
    ReaderDailyProceeding,
    StenoOrderWorkflow,
    StenoWorkflowSignature,
)
from apps.cis.models import OrderDetailsA
from apps.reader.workflow_state import apply_judge_decision, upsert_state_on_forward
from apps.core.bench_config import (
    BenchConfiguration,
    bench_slot_group,
    get_bench_configurations,
    get_forward_bench_keys_for_reader,
    mapped_judge_names_for_reader,
)


class ReaderBenchForwardTargetTest(TestCase):
    """
    reader_judge_assignment.reader_user_id must be the Django User.id of the reader.
    Bench configs use active bench_t + generic JUDGE (or legacy slot groups).
    """

    def setUp(self):
        self.today = timezone.localdate()
        self.reader = self._create_user(
            email="reader.single@example.com",
            username="reader_single",
            group_name="READER",
        )
        self.other_reader = self._create_user(
            email="reader.other@example.com",
            username="reader_other",
            group_name="READER",
        )
        self.judge_user = self._create_user(
            email="judge.single@example.com",
            username="judge_single",
            group_name="JUDGE",
        )
        self.judge = JudgeT.objects.create(
            user=self.judge_user,
            judge_code="SK-SINGLE",
            judge_name="Hon Single Judge",
            display="Single",
            date_of_joining=self.today,
        )
        ReaderJudgeAssignment.objects.create(
            judge=self.judge,
            reader_user=self.reader,
            effective_from=self.today,
        )
        BenchT.objects.create(
            bench_code="S1",
            bench_name="Single Bench",
            bench_type_code="S",
            judge_code=self.judge.judge_code,
            judge=self.judge,
            from_date=self.today,
        )

    def _create_user(
        self,
        *,
        email: str,
        username: str,
        group_name: str,
    ) -> User:
        user = User.objects.create_user(
            email=email,
            username=username,
            password="password123",
            first_name=username,
            last_name="User",
        )
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user

    def _auth_client(self, user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_forward_keys_use_reader_user_id_from_assignment(self):
        keys = get_forward_bench_keys_for_reader(
            self.reader,
            reader_group="READER",
        )
        self.assertEqual(keys, {"S1"})
        # Generic READER has no legacy bench token; unmapped user gets no forward keys.
        keys_other = get_forward_bench_keys_for_reader(
            self.other_reader,
            reader_group="READER",
        )
        self.assertEqual(keys_other, set())

    def test_bench_configurations_api_sets_forward_target_and_judge_names(self):
        client = self._auth_client(self.reader)
        resp = client.get(
            "/api/v1/reader/bench-configurations/"
            "?accessible_only=true&reader_group=READER",
        )
        self.assertEqual(resp.status_code, 200)
        items = resp.data["items"]
        forward = [i for i in items if i.get("is_forward_target")]
        self.assertTrue(forward, "expected a forward bench for mapped reader")
        self.assertTrue(
            any("Hon Single Judge" in (n or "") for f in forward for n in f.get("judge_names") or []),
        )
        self.assertTrue(
            any(f.get("bench_key") == "S1" for f in forward),
        )

    def test_judge_without_judge_group_excludes_bench_and_assignment(self):
        self.judge_user.groups.clear()
        group, _ = Group.objects.get_or_create(name="STAFF")
        self.judge_user.groups.add(group)
        configs = get_bench_configurations()
        self.assertFalse(
            any(self.reader.id in c.reader_user_ids for c in configs),
            "Assignment must not attach to configs when judge user lacks JUDGE_* group",
        )


class MappedJudgeNamesAssignmentFallbackTest(TestCase):
    """
    mapped_judge_names_for_reader narrows to judges tied to this reader via
    ReaderJudgeAssignment (active window), aligned with judge_names / judge_user_ids.
    """

    def test_maps_only_assigned_judge_from_assignment_alignment(self):
        today = timezone.localdate()
        reader = User.objects.create_user(
            email="map.reader@example.com",
            username="map_reader",
            password="password123",
        )
        grp_r, _ = Group.objects.get_or_create(name="READER")
        reader.groups.add(grp_r)
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        ju_cj = User.objects.create_user(
            email="map.cj@example.com",
            username="map_cj",
            password="password123",
        )
        ju_j1 = User.objects.create_user(
            email="map.j1@example.com",
            username="map_j1",
            password="password123",
        )
        ju_cj.groups.add(grp_j)
        ju_j1.groups.add(grp_j)
        j_cj = JudgeT.objects.create(
            user=ju_cj,
            judge_code="MAP-CJ",
            judge_name="Chief Justice",
            display="CJ",
            date_of_joining=today,
        )
        j_j1 = JudgeT.objects.create(
            user=ju_j1,
            judge_code="MAP-J1",
            judge_name="Justice Bhaskar",
            display="J1",
            date_of_joining=today,
        )
        ReaderJudgeAssignment.objects.create(
            judge=j_j1,
            reader_user=reader,
            effective_from=today,
        )
        cfg = BenchConfiguration(
            bench_key="MAP1",
            label="Division",
            bench_code="MAP1",
            bench_name="Map Bench",
            judge_names=("Hon Chief", "Hon Bhaskar"),
            judge_user_ids=(ju_cj.id, ju_j1.id),
            judge_groups=(bench_slot_group(0), bench_slot_group(1)),
            reader_user_ids=tuple(),
            reader_user_ids_by_group=tuple(),
        )
        names = mapped_judge_names_for_reader(cfg, reader)
        self.assertEqual(names, ("Hon Bhaskar",))


class ReaderBenchScopeIsolationTest(TestCase):
    """
    With multiple active benches, accessible_only bench-configurations lists only benches
    whose judges have an active ReaderJudgeAssignment to this reader.
    """

    def setUp(self):
        self.today = timezone.localdate()
        self.reader = User.objects.create_user(
            email="scope.reader@example.com",
            username="scope_reader",
            password="password123",
            first_name="Scope",
            last_name="Reader",
        )
        grp_r, _ = Group.objects.get_or_create(name="READER")
        self.reader.groups.add(grp_r)
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        self.judge_user_a = User.objects.create_user(
            email="scope.judge.a@example.com",
            username="scope_judge_a",
            password="password123",
            first_name="A",
            last_name="Judge",
        )
        self.judge_user_a.groups.add(grp_j)
        self.judge_user_b = User.objects.create_user(
            email="scope.judge.b@example.com",
            username="scope_judge_b",
            password="password123",
            first_name="B",
            last_name="Judge",
        )
        self.judge_user_b.groups.add(grp_j)
        self.judge_a = JudgeT.objects.create(
            user=self.judge_user_a,
            judge_code="SCOPE-A",
            judge_name="Judge Alpha",
            display="A",
            date_of_joining=self.today,
        )
        self.judge_b = JudgeT.objects.create(
            user=self.judge_user_b,
            judge_code="SCOPE-B",
            judge_name="Judge Beta",
            display="B",
            date_of_joining=self.today,
        )
        ReaderJudgeAssignment.objects.create(
            judge=self.judge_a,
            reader_user=self.reader,
            effective_from=self.today,
        )
        BenchT.objects.create(
            bench_code="SA",
            bench_name="Bench A",
            bench_type_code="S",
            judge_code=self.judge_a.judge_code,
            judge=self.judge_a,
            from_date=self.today,
        )
        BenchT.objects.create(
            bench_code="SB",
            bench_name="Bench B",
            bench_type_code="S",
            judge_code=self.judge_b.judge_code,
            judge=self.judge_b,
            from_date=self.today,
        )

    def _auth_client(self, user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_bench_configurations_accessible_only_single_bench_for_mapped_reader(self):
        client = self._auth_client(self.reader)
        resp = client.get(
            "/api/v1/reader/bench-configurations/"
            "?accessible_only=true&reader_group=READER",
        )
        self.assertEqual(resp.status_code, 200)
        keys = {item["bench_key"] for item in resp.data["items"]}
        self.assertEqual(keys, {"SA"}, msg=resp.data)
        self.assertEqual(len(resp.data["items"]), 1)
        row = resp.data["items"][0]
        self.assertEqual(row.get("mapped_judge_names"), ["Judge Alpha"])

    def test_registered_cases_empty_when_reader_has_no_bench_scope_match(self):
        """No bench filter rows when reader has no assignment to any configured bench."""
        orphan = User.objects.create_user(
            email="orphan.reader@example.com",
            username="orphan_reader",
            password="password123",
            first_name="Orphan",
            last_name="Reader",
        )
        grp_r, _ = Group.objects.get_or_create(name="READER")
        orphan.groups.add(grp_r)
        client = self._auth_client(orphan)
        resp = client.get("/api/v1/reader/registered-cases/?page_size=50&reader_group=READER")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("total"), 0)


class ReaderRegisteredCasesPreForwardVisibilityTest(TestCase):
    """
    ACCEPTED filings with a registration bench matching ReaderJudgeAssignment appear on
    /reader/registered-cases/ before any CourtroomForward; other bench keys do not.
    """

    def setUp(self):
        self.today = timezone.localdate()
        self.reader = User.objects.create_user(
            email="prefwd.reader@example.com",
            username="prefwd_reader",
            password="password123",
            first_name="Pre",
            last_name="Forward",
        )
        grp_r, _ = Group.objects.get_or_create(name="READER")
        self.reader.groups.add(grp_r)
        grp_j, _ = Group.objects.get_or_create(name="JUDGE")
        self.judge_user = User.objects.create_user(
            email="prefwd.judge@example.com",
            username="prefwd_judge",
            password="password123",
            first_name="Bench",
            last_name="Judge",
        )
        self.judge_user.groups.add(grp_j)
        self.judge = JudgeT.objects.create(
            user=self.judge_user,
            judge_code="PRE-FWD",
            judge_name="Mapped Judge",
            display="MJ",
            date_of_joining=self.today,
        )
        ReaderJudgeAssignment.objects.create(
            judge=self.judge,
            reader_user=self.reader,
            effective_from=self.today,
        )
        BenchT.objects.create(
            bench_code="PRE1",
            bench_name="Pre Forward Bench",
            bench_type_code="S",
            judge_code=self.judge.judge_code,
            judge=self.judge,
            from_date=self.today,
        )
        self.ef_on_mapped_bench = Efiling.objects.create(
            is_draft=False,
            status="ACCEPTED",
            bench="PRE1",
            case_number="WP/PREFWD/1/2026",
            petitioner_name="Petitioner One",
            petitioner_contact="9876500001",
            petitioner_vs_respondent="P1 v R",
            accepted_at=timezone.now(),
        )
        self.ef_other_bench_key = Efiling.objects.create(
            is_draft=False,
            status="ACCEPTED",
            bench="OTHER",
            case_number="WP/PREFWD/2/2026",
            petitioner_name="Petitioner Two",
            petitioner_contact="9876500002",
            petitioner_vs_respondent="P2 v R",
            accepted_at=timezone.now(),
        )

    def _auth_client(self, user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_registered_case_visible_before_forward_scoped_to_bench(self):
        self.assertEqual(
            CourtroomForward.objects.filter(
                efiling_id__in=[
                    self.ef_on_mapped_bench.id,
                    self.ef_other_bench_key.id,
                ],
            ).count(),
            0,
        )

        client = self._auth_client(self.reader)
        resp = client.get(
            "/api/v1/reader/registered-cases/?page_size=50&reader_group=READER",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("total"), 1)
        items = resp.data.get("items") or []
        ids = {row["efiling_id"] for row in items}
        self.assertIn(self.ef_on_mapped_bench.id, ids)
        self.assertNotIn(self.ef_other_bench_key.id, ids)
        row = next(r for r in items if r["efiling_id"] == self.ef_on_mapped_bench.id)
        self.assertEqual(row.get("approval_status"), "NOT_FORWARDED")
        self.assertEqual(row.get("overall_status"), "not_forwarded")
        self.assertEqual(row.get("my_forward_status"), "not_forwarded")
        self.assertEqual(row.get("bench_has_forward"), False)


class ReaderDivisionBenchAuthorityTest(TestCase):
    def setUp(self):
        self.forwarded_for_date = timezone.localdate()
        self.listing_date = self.forwarded_for_date + timedelta(days=7)

        self.reader_cj = self._create_user(
            email="reader.cj@example.com",
            username="reader_cj",
            group_name="READER",
        )
        self.reader_j1 = self._create_user(
            email="reader.j1@example.com",
            username="reader_j1",
            group_name="READER",
        )
        self.judge_cj_user = self._create_user(
            email="judge.cj@example.com",
            username="judge_cj",
            group_name="JUDGE",
        )
        self.judge_j1_user = self._create_user(
            email="judge.j1@example.com",
            username="judge_j1",
            group_name="JUDGE",
        )
        self.steno_user = self._create_user(
            email="steno@example.com",
            username="steno_user",
            group_name="API_STENOGRAPHER",
        )

        self.judge_cj = JudgeT.objects.create(
            user=self.judge_cj_user,
            judge_code="SK0",
            judge_name="Chief Justice",
            display="Chief Justice",
            date_of_joining=self.forwarded_for_date,
        )
        self.judge_j1 = JudgeT.objects.create(
            user=self.judge_j1_user,
            judge_code="HSK0002",
            judge_name="Judge I",
            display="Judge I",
            date_of_joining=self.forwarded_for_date,
        )

        ReaderJudgeAssignment.objects.create(
            judge=self.judge_cj,
            reader_user=self.reader_cj,
            effective_from=self.forwarded_for_date,
        )
        ReaderJudgeAssignment.objects.create(
            judge=self.judge_j1,
            reader_user=self.reader_j1,
            effective_from=self.forwarded_for_date,
        )
        JudgeStenoMapping.objects.create(
            judge=self.judge_cj,
            steno_user=self.steno_user,
            bench_key=None,
            effective_from=self.forwarded_for_date,
        )

        BenchT.objects.create(
            bench_code="DB1",
            bench_name="Division Bench I",
            bench_type_code="DB",
            judge_code=self.judge_cj.judge_code,
            judge=self.judge_cj,
            from_date=self.forwarded_for_date,
        )
        BenchT.objects.create(
            bench_code="DB1",
            bench_name="Division Bench I",
            bench_type_code="DB",
            judge_code=self.judge_j1.judge_code,
            judge=self.judge_j1,
            from_date=self.forwarded_for_date,
        )

        self.filing = Efiling.objects.create(
            case_number="DB-CASE-001",
            e_filing_number="ASK20260000001C202600001",
            bench="DB1",
            petitioner_name="Petitioner",
            petitioner_contact="9876543210",
            is_draft=False,
            status="ACCEPTED",
        )

        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S0",
            listing_summary="Division bench summary",
            forwarded_by=self.reader_cj,
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S1",
            listing_summary="Division bench summary",
            forwarded_by=self.reader_j1,
        )

        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_cj_user,
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            bench_role_group="BENCH_S0",
        )
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_j1_user,
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            bench_role_group="BENCH_S1",
        )
        upsert_state_on_forward(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            forwarded_by=self.reader_cj,
        )
    def _create_user(
        self,
        *,
        email: str,
        username: str,
        group_name: str,
    ) -> User:
        user = User.objects.create_user(
            email=email,
            username=username,
            password="password123",
            first_name=username,
            last_name="User",
        )
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user

    def _auth_client(self, user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_lower_priority_reader_can_view_case_but_not_assign_date(self):
        client = self._auth_client(self.reader_j1)

        list_response = client.get(
            "/api/v1/reader/registered-cases/"
            "?page_size=10&reader_group=READER"
        )

        self.assertEqual(list_response.status_code, 200)
        case_item = next(
            item
            for item in list_response.data["items"]
            if item["efiling_id"] == self.filing.id
        )
        self.assertEqual(case_item["approval_status"], "APPROVED")
        self.assertFalse(case_item["can_assign_listing_date"])

        assign_response = client.post(
            "/api/v1/reader/assign-date/?reader_group=READER",
            {
                "efiling_ids": [self.filing.id],
                "listing_date": self.listing_date.isoformat(),
                "forwarded_for_date": self.forwarded_for_date.isoformat(),
                "listing_remark": "Attempt by lower-priority reader",
            },
            format="json",
        )

        self.assertEqual(assign_response.status_code, 400)
        err = assign_response.data["efiling_ids"]
        err_msg = err[0] if isinstance(err, (list, tuple)) else err
        self.assertIn("higher-priority bench reader", str(err_msg))
        self.assertFalse(
            CourtroomJudgeDecision.objects.filter(
                efiling=self.filing,
                forwarded_for_date=self.forwarded_for_date,
                listing_date__isnull=False,
            ).exists()
        )

    def test_single_forward_other_reader_sees_aggregate_bench_status(self):
        """If only one reader created a forward, the other still sees combined judge state."""
        CourtroomForward.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            forwarded_by=self.reader_j1,
        ).delete()
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
        ).delete()

        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "PENDING")
        self.assertEqual(j1_case["approval_status"], "PENDING")
        self.assertEqual(cj_case["overall_status"], "in_review")
        self.assertEqual(j1_case["overall_status"], "in_review")
        self.assertEqual(cj_case["my_forward_status"], "forwarded")
        self.assertEqual(j1_case["my_forward_status"], "not_forwarded")
        self.assertTrue(cj_case["bench_has_forward"])
        self.assertTrue(j1_case["bench_has_forward"])
        self.assertEqual(
            j1_case["judge_status_by_role"].get("BENCH_S0"),
            "pending",
        )
        self.assertEqual(
            j1_case["judge_status_by_role"].get("BENCH_S1"),
            "pending",
        )

    def test_higher_priority_reader_can_assign_date_for_division_bench(self):
        client = self._auth_client(self.reader_cj)

        list_response = client.get(
            "/api/v1/reader/registered-cases/"
            "?page_size=10&reader_group=READER"
        )

        self.assertEqual(list_response.status_code, 200)
        case_item = next(
            item
            for item in list_response.data["items"]
            if item["efiling_id"] == self.filing.id
        )
        self.assertTrue(case_item["can_assign_listing_date"])

        assign_response = client.post(
            "/api/v1/reader/assign-date/?reader_group=READER",
            {
                "efiling_ids": [self.filing.id],
                "listing_date": self.listing_date.isoformat(),
                "forwarded_for_date": self.forwarded_for_date.isoformat(),
                "listing_remark": "Final division bench date",
            },
            format="json",
        )

        self.assertEqual(assign_response.status_code, 200)
        self.assertEqual(assign_response.data["updated"], 2)
        self.assertEqual(
            CourtroomJudgeDecision.objects.filter(
                efiling=self.filing,
                forwarded_for_date=self.forwarded_for_date,
                listing_date=self.listing_date,
            ).count(),
            2,
        )

    def test_both_readers_see_approved_after_both_judges_approve(self):
        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "APPROVED")
        self.assertEqual(j1_case["approval_status"], "APPROVED")
        self.assertEqual(cj_case["overall_status"], "ready_for_listing")
        self.assertEqual(j1_case["overall_status"], "ready_for_listing")
        self.assertTrue(cj_case["all_judges_reviewed"])
        self.assertTrue(j1_case["all_judges_reviewed"])
        self.assertEqual(cj_case["judge_status_by_role"].get("BENCH_S0"), "approved")
        self.assertEqual(cj_case["judge_status_by_role"].get("BENCH_S1"), "approved")

    def test_each_reader_only_sees_own_listing_summary_text(self):
        CourtroomForward.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
        ).delete()
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S0",
            listing_summary="Only for CJ reader eyes",
            forwarded_by=self.reader_cj,
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S1",
            listing_summary="Only for J1 reader eyes",
            forwarded_by=self.reader_j1,
        )
        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case.get("listing_summary"), "Only for CJ reader eyes")
        self.assertEqual(j1_case.get("listing_summary"), "Only for J1 reader eyes")

    def test_listing_summary_resolves_by_slot_when_forwarded_by_unset(self):
        """Division bench: slot (bench_role_group) identifies the row if forwarded_by is null."""
        CourtroomForward.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
        ).delete()
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S0",
            listing_summary="S0 text",
            forwarded_by=None,
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S1",
            listing_summary="S1 text",
            forwarded_by=None,
        )
        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case.get("listing_summary"), "S0 text")
        self.assertEqual(j1_case.get("listing_summary"), "S1 text")

    def test_api_forward_per_slot_preserves_both_summaries(self):
        CourtroomForward.objects.filter(efiling=self.filing).delete()
        CourtroomJudgeDecision.objects.filter(efiling=self.filing).delete()
        d = self.forwarded_for_date.isoformat()
        base_payload = {
            "efiling_ids": [self.filing.id],
            "bench_key": "DB1",
            "forwarded_for_date": d,
        }
        cj = self._auth_client(self.reader_cj)
        r1 = cj.post(
            "/api/v1/reader/forward/?reader_group=READER",
            {**base_payload, "listing_summary": "Summary from reader slot S0"},
            format="json",
        )
        self.assertEqual(r1.status_code, 200, r1.data)
        j1 = self._auth_client(self.reader_j1)
        r2 = j1.post(
            "/api/v1/reader/forward/?reader_group=READER",
            {**base_payload, "listing_summary": "Summary from reader slot S1"},
            format="json",
        )
        self.assertEqual(r2.status_code, 200, r2.data)
        rows = list(
            CourtroomForward.objects.filter(
                efiling=self.filing,
                forwarded_for_date=self.forwarded_for_date,
                bench_key="DB1",
            ).order_by("bench_role_group")
        )
        self.assertEqual(len(rows), 2)
        by_slot = {r.bench_role_group: (r.listing_summary or "").strip() for r in rows}
        self.assertEqual(by_slot["BENCH_S0"], "Summary from reader slot S0")
        self.assertEqual(by_slot["BENCH_S1"], "Summary from reader slot S1")

    def test_both_readers_pending_when_only_one_judge_approved(self):
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            judge_user=self.judge_j1_user,
        ).delete()
        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "PENDING")
        self.assertEqual(j1_case["approval_status"], "PENDING")
        self.assertEqual(cj_case["overall_status"], "in_review")
        self.assertEqual(j1_case["overall_status"], "in_review")
        self.assertFalse(cj_case["all_judges_reviewed"])
        self.assertFalse(j1_case["all_judges_reviewed"])

    def test_decisions_wrong_forwarded_for_date_do_not_aggregate(self):
        """Judge decisions must use the same forwarded_for_date as the forward row."""
        wrong = self.forwarded_for_date + timedelta(days=1)
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
        ).update(forwarded_for_date=wrong)

        cj_client = self._auth_client(self.reader_cj)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "PENDING")
        self.assertFalse(cj_case["all_judges_reviewed"])
        self.assertEqual(cj_case["overall_status"], "in_review")
        self.assertEqual(cj_case["judge_status_by_role"].get("BENCH_S0"), "pending")
        self.assertEqual(cj_case["judge_status_by_role"].get("BENCH_S1"), "pending")

    def test_division_bench_notes_preserve_distinct_judge_labels(self):
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            judge_user=self.judge_cj_user,
        ).update(decision_notes="CJ approved")
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            judge_user=self.judge_j1_user,
        ).update(decision_notes="J1 approved")

        for reader in (self.reader_cj, self.reader_j1):
            client = self._auth_client(reader)
            list_response = client.get(
                "/api/v1/reader/registered-cases/?page_size=10&reader_group=READER"
            )
            self.assertEqual(list_response.status_code, 200)
            case_item = next(
                item
                for item in list_response.data["items"]
                if item["efiling_id"] == self.filing.id
            )
            self.assertEqual(case_item["approval_status"], "APPROVED")
            notes = case_item.get("approval_notes") or []
            blob = " ".join(notes)
            self.assertIn("CJ approved", blob)
            self.assertIn("J1 approved", blob)

    def test_reader_daily_proceeding_submit_creates_steno_workflow(self):
        client = self._auth_client(self.reader_cj)
        response = client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER",
            {
                "efiling_id": self.filing.id,
                "hearing_date": self.forwarded_for_date.isoformat(),
                "next_listing_date": self.listing_date.isoformat(),
                "proceedings_text": "Matter heard.",
                "reader_remark": "Send draft order.",
                "document_type": "ORDER",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        proceeding = ReaderDailyProceeding.objects.get(efiling=self.filing)
        workflow = StenoOrderWorkflow.objects.get(proceeding=proceeding, document_type="ORDER")
        self.assertEqual(workflow.assigned_steno_id, self.steno_user.id)
        self.assertEqual(workflow.workflow_status, StenoOrderWorkflow.WorkflowStatus.PENDING_UPLOAD)

    def test_reader_daily_proceeding_submit_routes_listing_and_steno_remarks_separately(self):
        client = self._auth_client(self.reader_cj)
        response = client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER",
            {
                "efiling_id": self.filing.id,
                "hearing_date": self.forwarded_for_date.isoformat(),
                "next_listing_date": self.listing_date.isoformat(),
                "proceedings_text": "Matter heard.",
                "steno_remark": "Prepare order draft for corrections.",
                "listing_remark": "List this after two weeks.",
                "document_type": "ORDER",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        proceeding = ReaderDailyProceeding.objects.get(efiling=self.filing)
        self.assertEqual(
            (proceeding.steno_remark or "").strip(),
            "Prepare order draft for corrections.",
        )
        self.assertEqual(
            (proceeding.listing_remark or "").strip(),
            "List this after two weeks.",
        )
        decision = CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
        ).first()
        self.assertIsNotNone(decision)
        self.assertEqual(
            (decision.reader_listing_remark or "").strip(),
            "List this after two weeks.",
        )

    def test_forward_creates_bench_workflow_state(self):
        state = BenchWorkflowState.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
        ).first()
        self.assertIsNotNone(state)
        self.assertEqual(state.required_role_groups, ["BENCH_S0", "BENCH_S1"])

    def test_bench_configurations_forward_target_for_division_mapped_readers(self):
        """Division bench_code DB1; forward keys use that bench bucket."""
        for user in (self.reader_cj, self.reader_j1):
            client = self._auth_client(user)
            resp = client.get(
                "/api/v1/reader/bench-configurations/"
                "?accessible_only=true&reader_group=READER"
            )
            self.assertEqual(resp.status_code, 200, msg=getattr(resp, "data", None))
            forward = [i for i in resp.data["items"] if i.get("is_forward_target")]
            self.assertEqual(len(forward), 1, msg=f"user={user.id}")
            self.assertEqual(forward[0]["bench_key"], "DB1")
            names = " ".join(forward[0].get("judge_names") or [])
            self.assertIn("Chief Justice", names)
            self.assertIn("Judge I", names)

    def test_judge_decisions_dual_write_to_bench_workflow_state(self):
        cj_decision = CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_role_group="BENCH_S0",
        ).first()
        j1_decision = CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_role_group="BENCH_S1",
        ).first()
        self.assertIsNotNone(cj_decision)
        self.assertIsNotNone(j1_decision)
        apply_judge_decision(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S0",
            judge_user_id=self.judge_cj_user.id,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            decision_notes=None,
        )
        apply_judge_decision(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
            bench_role_group="BENCH_S1",
            judge_user_id=self.judge_j1_user.id,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            decision_notes=None,
        )
        state = BenchWorkflowState.objects.get(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="DB1",
        )
        self.assertTrue((state.decision_by_role or {}).get("BENCH_S0", {}).get("approved"))
        self.assertTrue((state.decision_by_role or {}).get("BENCH_S1", {}).get("approved"))

    def test_daily_proceedings_list_includes_only_published_cases_for_selected_date(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.listing_date,
            bench_key="DB1",
            status=CauseList.CauseListStatus.PUBLISHED,
        )
        CauseListEntry.objects.create(
            cause_list=cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        client = self._auth_client(self.reader_cj)
        resp = client.get(
            "/api/v1/reader/daily-proceedings/"
            f"?reader_group=READER&cause_list_date={self.listing_date.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [row["efiling_id"] for row in resp.data["items"]]
        self.assertIn(self.filing.id, ids)

    def test_daily_proceedings_list_excludes_non_published_or_other_date(self):
        draft_cause_list = CauseList.objects.create(
            cause_list_date=self.listing_date,
            bench_key="DB1",
            status=CauseList.CauseListStatus.DRAFT,
        )
        CauseListEntry.objects.create(
            cause_list=draft_cause_list,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        published_other_date = CauseList.objects.create(
            cause_list_date=self.listing_date + timedelta(days=1),
            bench_key="DB1",
            status=CauseList.CauseListStatus.PUBLISHED,
        )
        CauseListEntry.objects.create(
            cause_list=published_other_date,
            efiling=self.filing,
            included=True,
            serial_no=1,
        )
        client = self._auth_client(self.reader_cj)
        resp = client.get(
            "/api/v1/reader/daily-proceedings/"
            f"?reader_group=READER&cause_list_date={self.listing_date.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [row["efiling_id"] for row in resp.data["items"]]
        self.assertNotIn(self.filing.id, ids)

    @override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
    def test_steno_upload_draft_file_creates_index_and_queue_url(self):
        reader_client = self._auth_client(self.reader_cj)
        reader_client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER",
            {
                "efiling_id": self.filing.id,
                "hearing_date": self.forwarded_for_date.isoformat(),
                "next_listing_date": self.listing_date.isoformat(),
                "proceedings_text": "Matter heard.",
                "reader_remark": "Send draft order.",
                "document_type": "ORDER",
            },
            format="json",
        )
        workflow = StenoOrderWorkflow.objects.get(efiling=self.filing, document_type="ORDER")
        steno_client = self._auth_client(self.steno_user)
        pdf = SimpleUploadedFile("draft.pdf", b"%PDF-1.4\n%", content_type="application/pdf")
        up = steno_client.post(
            "/api/v1/reader/steno/upload-draft-file/",
            {"workflow_id": str(workflow.id), "file": pdf},
            format="multipart",
        )
        self.assertEqual(up.status_code, 200, up.data)
        workflow.refresh_from_db()
        self.assertEqual(workflow.workflow_status, StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO)
        self.assertIn("draft_order_no", up.data)
        self.assertTrue(up.data.get("draft_preview_url"))
        row = OrderDetailsA.objects.filter(hashkey=f"STENO_WF_{workflow.id}_DRAFT").first()
        self.assertIsNotNone(row)

        q = steno_client.get("/api/v1/reader/steno/queue/")
        self.assertEqual(q.status_code, 200)
        item = next(row for row in q.data["items"] if row["workflow_id"] == workflow.id)
        self.assertIsNotNone(item.get("draft_order_no"))
        self.assertTrue(item.get("draft_preview_url"))

    @override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
    def test_steno_upload_signed_publish_after_judge_approval(self):
        reader_client = self._auth_client(self.reader_cj)
        reader_client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER",
            {
                "efiling_id": self.filing.id,
                "hearing_date": self.forwarded_for_date.isoformat(),
                "next_listing_date": self.listing_date.isoformat(),
                "proceedings_text": "Matter heard.",
                "reader_remark": "Send draft order.",
                "document_type": "ORDER",
            },
            format="json",
        )
        workflow = StenoOrderWorkflow.objects.get(efiling=self.filing, document_type="ORDER")
        steno_client = self._auth_client(self.steno_user)
        draft_pdf = SimpleUploadedFile("draft.pdf", b"%PDF-1.4\n%", content_type="application/pdf")
        steno_client.post(
            "/api/v1/reader/steno/upload-draft-file/",
            {"workflow_id": str(workflow.id), "file": draft_pdf},
            format="multipart",
        )
        steno_client.post(
            "/api/v1/reader/steno/submit-judge/",
            {"workflow_id": workflow.id},
            format="json",
        )
        workflow.refresh_from_db()
        workflow.workflow_status = StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED
        workflow.judge_approval_status = StenoOrderWorkflow.JudgeApprovalStatus.APPROVED
        workflow.save(update_fields=["workflow_status", "judge_approval_status", "updated_at"])

        signed_pdf = SimpleUploadedFile("signed.pdf", b"%PDF-1.4\n%", content_type="application/pdf")
        resp = steno_client.post(
            "/api/v1/reader/steno/upload-signed-publish/",
            {
                "workflow_id": str(workflow.id),
                "file": signed_pdf,
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        workflow.refresh_from_db()
        self.assertEqual(workflow.workflow_status, StenoOrderWorkflow.WorkflowStatus.SIGNED_AND_PUBLISHED)
        self.assertIsNotNone(workflow.published_at)
        self.assertIsNotNone(workflow.digitally_signed_at)
        self.assertIn("signed_order_no", resp.data)
        self.assertTrue(resp.data.get("signed_preview_url"))
        signed_row = OrderDetailsA.objects.filter(hashkey=f"STENO_WF_{workflow.id}_SIGNED_FINAL").first()
        self.assertIsNotNone(signed_row)

    def test_share_approved_draft_requires_primary_steno(self):
        workflow = StenoOrderWorkflow.objects.create(
            proceeding=ReaderDailyProceeding.objects.create(
                efiling=self.filing,
                bench_key="DB1",
                hearing_date=self.forwarded_for_date,
                next_listing_date=self.listing_date,
                proceedings_text="Matter heard.",
            ),
            efiling=self.filing,
            assigned_steno=self.steno_user,
            workflow_status=StenoOrderWorkflow.WorkflowStatus.JUDGE_APPROVED,
            judge_approval_status=StenoOrderWorkflow.JudgeApprovalStatus.APPROVED,
            document_type="ORDER",
        )
        other_steno = User.objects.create_user(
            email="other.steno@example.com",
            username="other_steno",
            password="password123",
        )
        JudgeStenoMapping.objects.create(
            judge=self.judge_cj,
            steno_user=self.steno_user,
            bench_key="DB1",
            effective_from=self.forwarded_for_date,
        )
        JudgeStenoMapping.objects.create(
            judge=self.judge_j1,
            steno_user=other_steno,
            bench_key="DB1",
            effective_from=self.forwarded_for_date,
        )

        other_client = self._auth_client(other_steno)
        denied = other_client.post(
            "/api/v1/reader/steno/share-approved-draft/",
            {"workflow_id": workflow.id},
            format="json",
        )
        self.assertEqual(denied.status_code, 400)

        primary_client = self._auth_client(self.steno_user)
        ok = primary_client.post(
            "/api/v1/reader/steno/share-approved-draft/",
            {"workflow_id": workflow.id},
            format="json",
        )
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(
            StenoWorkflowSignature.objects.filter(workflow=workflow).exists()
        )
