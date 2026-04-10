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
from apps.core.models import EfilingDocumentsIndex
from apps.listing.models import CauseList, CauseListEntry
from apps.reader.models import BenchWorkflowState, CourtroomForward, ReaderDailyProceeding, StenoOrderWorkflow
from apps.reader.workflow_state import apply_judge_decision, upsert_state_on_forward


class ReaderDivisionBenchAuthorityTest(TestCase):
    def setUp(self):
        self.forwarded_for_date = timezone.localdate()
        self.listing_date = self.forwarded_for_date + timedelta(days=7)

        self.reader_cj = self._create_user(
            email="reader.cj@example.com",
            username="reader_cj",
            group_name="READER_CJ",
        )
        self.reader_j1 = self._create_user(
            email="reader.j1@example.com",
            username="reader_j1",
            group_name="READER_J1",
        )
        self.judge_cj_user = self._create_user(
            email="judge.cj@example.com",
            username="judge_cj",
            group_name="JUDGE_CJ",
        )
        self.judge_j1_user = self._create_user(
            email="judge.j1@example.com",
            username="judge_j1",
            group_name="JUDGE_J1",
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
            bench_key="CJ",
            listing_summary="Division bench summary",
            forwarded_by=self.reader_cj,
        )
        CourtroomForward.objects.create(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="Judge1",
            listing_summary="Division bench summary",
            forwarded_by=self.reader_j1,
        )

        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_cj_user,
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            bench_role_group="JUDGE_CJ",
        )
        CourtroomJudgeDecision.objects.create(
            judge_user=self.judge_j1_user,
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            bench_role_group="JUDGE_J1",
        )
        upsert_state_on_forward(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="CJ",
            forwarded_by=self.reader_cj,
        )
        upsert_state_on_forward(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="Judge1",
            forwarded_by=self.reader_j1,
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
            "?page_size=10&reader_group=READER_J1"
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
            "/api/v1/reader/assign-date/?reader_group=READER_J1",
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

    def test_only_one_reader_forward_keeps_other_reader_not_forwarded(self):
        CourtroomForward.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="Judge1",
        ).delete()
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
        ).delete()

        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER_CJ")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER_J1")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "PENDING")
        self.assertEqual(j1_case["approval_status"], "NOT_FORWARDED")

    def test_higher_priority_reader_can_assign_date_for_division_bench(self):
        client = self._auth_client(self.reader_cj)

        list_response = client.get(
            "/api/v1/reader/registered-cases/"
            "?page_size=10&reader_group=READER_CJ"
        )

        self.assertEqual(list_response.status_code, 200)
        case_item = next(
            item
            for item in list_response.data["items"]
            if item["efiling_id"] == self.filing.id
        )
        self.assertTrue(case_item["can_assign_listing_date"])

        assign_response = client.post(
            "/api/v1/reader/assign-date/?reader_group=READER_CJ",
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
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER_CJ")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER_J1")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "APPROVED")
        self.assertEqual(j1_case["approval_status"], "APPROVED")

    def test_both_readers_pending_when_only_one_judge_approved(self):
        CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            judge_user=self.judge_j1_user,
        ).delete()
        cj_client = self._auth_client(self.reader_cj)
        j1_client = self._auth_client(self.reader_j1)
        cj_resp = cj_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER_CJ")
        j1_resp = j1_client.get("/api/v1/reader/registered-cases/?page_size=10&reader_group=READER_J1")
        cj_case = next(item for item in cj_resp.data["items"] if item["efiling_id"] == self.filing.id)
        j1_case = next(item for item in j1_resp.data["items"] if item["efiling_id"] == self.filing.id)
        self.assertEqual(cj_case["approval_status"], "PENDING")
        self.assertEqual(j1_case["approval_status"], "PENDING")

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

        for reader, group in (
            (self.reader_cj, "READER_CJ"),
            (self.reader_j1, "READER_J1"),
        ):
            client = self._auth_client(reader)
            list_response = client.get(
                f"/api/v1/reader/registered-cases/?page_size=10&reader_group={group}"
            )
            self.assertEqual(list_response.status_code, 200)
            case_item = next(
                item
                for item in list_response.data["items"]
                if item["efiling_id"] == self.filing.id
            )
            self.assertEqual(case_item["approval_status"], "APPROVED")
            notes = case_item.get("approval_notes") or []
            self.assertTrue(any(n.startswith("Judge CJ:") for n in notes))
            self.assertTrue(any(n.startswith("Judge J1:") for n in notes))

    def test_reader_daily_proceeding_submit_creates_steno_workflow(self):
        client = self._auth_client(self.reader_cj)
        response = client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER_CJ",
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

    def test_forward_creates_bench_workflow_state(self):
        state = BenchWorkflowState.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="CJ",
        ).first()
        self.assertIsNotNone(state)
        self.assertEqual(state.required_role_groups, ["JUDGE_CJ"])

    def test_judge_decisions_dual_write_to_bench_workflow_state(self):
        cj_decision = CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_role_group="JUDGE_CJ",
        ).first()
        j1_decision = CourtroomJudgeDecision.objects.filter(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_role_group="JUDGE_J1",
        ).first()
        self.assertIsNotNone(cj_decision)
        self.assertIsNotNone(j1_decision)
        apply_judge_decision(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="CJ",
            bench_role_group="JUDGE_CJ",
            judge_user_id=self.judge_cj_user.id,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            decision_notes=None,
        )
        apply_judge_decision(
            efiling_id=self.filing.id,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="Judge1",
            bench_role_group="JUDGE_J1",
            judge_user_id=self.judge_j1_user.id,
            status=CourtroomJudgeDecision.DecisionStatus.APPROVED,
            approved=True,
            decision_notes=None,
        )
        state_cj = BenchWorkflowState.objects.get(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="CJ",
        )
        state_j1 = BenchWorkflowState.objects.get(
            efiling=self.filing,
            forwarded_for_date=self.forwarded_for_date,
            bench_key="Judge1",
        )
        self.assertTrue((state_cj.decision_by_role or {}).get("JUDGE_CJ", {}).get("approved"))
        self.assertTrue((state_j1.decision_by_role or {}).get("JUDGE_J1", {}).get("approved"))

    def test_daily_proceedings_list_includes_only_published_cases_for_selected_date(self):
        cause_list = CauseList.objects.create(
            cause_list_date=self.listing_date,
            bench_key="CJ+Judge1",
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
            f"?reader_group=READER_CJ&cause_list_date={self.listing_date.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [row["efiling_id"] for row in resp.data["items"]]
        self.assertIn(self.filing.id, ids)

    def test_daily_proceedings_list_excludes_non_published_or_other_date(self):
        draft_cause_list = CauseList.objects.create(
            cause_list_date=self.listing_date,
            bench_key="CJ+Judge1",
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
            bench_key="CJ+Judge1",
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
            f"?reader_group=READER_CJ&cause_list_date={self.listing_date.isoformat()}"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [row["efiling_id"] for row in resp.data["items"]]
        self.assertNotIn(self.filing.id, ids)

    @override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
    def test_steno_upload_draft_file_creates_index_and_queue_url(self):
        reader_client = self._auth_client(self.reader_cj)
        reader_client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER_CJ",
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
        self.assertIsNotNone(workflow.draft_document_index_id)
        self.assertEqual(workflow.workflow_status, StenoOrderWorkflow.WorkflowStatus.UPLOADED_BY_STENO)
        idx = EfilingDocumentsIndex.objects.filter(id=workflow.draft_document_index_id).first()
        self.assertIsNotNone(idx)
        self.assertEqual(idx.document.e_filing_id, self.filing.id)

        q = steno_client.get("/api/v1/reader/steno/queue/")
        self.assertEqual(q.status_code, 200)
        item = next(row for row in q.data["items"] if row["workflow_id"] == workflow.id)
        self.assertEqual(item["draft_document_index_id"], workflow.draft_document_index_id)
        self.assertIn("/api/v1/efiling/efiling-documents-index/", item["draft_preview_url"])

    @override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
    def test_steno_upload_signed_publish_after_judge_approval(self):
        reader_client = self._auth_client(self.reader_cj)
        reader_client.post(
            "/api/v1/reader/daily-proceedings/submit/?reader_group=READER_CJ",
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
                "signature_provider": "eSign",
                "certificate_serial": "CERT-12345",
                "signer_name": "Steno User",
                "signature_reason": "Approved draft signed",
                "signature_txn_id": "TXN-001",
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        workflow.refresh_from_db()
        self.assertEqual(workflow.workflow_status, StenoOrderWorkflow.WorkflowStatus.SIGNED_AND_PUBLISHED)
        self.assertIsNotNone(workflow.signed_document_index_id)
        self.assertIsNotNone(workflow.published_at)
        self.assertEqual(workflow.digital_signature_provider, "eSign")
        self.assertEqual(workflow.digital_signature_certificate_serial, "CERT-12345")
        self.assertEqual(workflow.digital_signature_signer_name, "Steno User")
        self.assertEqual(workflow.digital_signature_reason, "Approved draft signed")
        self.assertIsNotNone(workflow.digitally_signed_at)
        self.assertEqual(
            (workflow.digital_signature_metadata or {}).get("signature_txn_id"),
            "TXN-001",
        )
