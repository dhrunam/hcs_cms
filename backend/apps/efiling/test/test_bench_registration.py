"""Canonical bench resolution for case registration (reader routing)."""

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.core.bench_config import resolve_bench_for_registration
from apps.core.models import (
    BenchT,
    CaseTypeT,
    Efiling,
    EfilingDocuments,
    EfilingDocumentsIndex,
    JudgeT,
)
from apps.efiling.review_utils import finalize_approved_filing


class ResolveBenchForRegistrationTest(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.user = User.objects.create_user(
            email="reg.judge@example.com",
            username="reg_judge",
            password="x",
        )
        grp, _ = Group.objects.get_or_create(name="JUDGE")
        self.user.groups.add(grp)
        self.judge = JudgeT.objects.create(
            user=self.user,
            judge_code="REG-J1",
            judge_name="Reg Judge",
            display="RJ",
            date_of_joining=self.today,
        )
        BenchT.objects.create(
            bench_code="REG01",
            bench_name="Reg Bench",
            bench_type_code="S",
            judge_code=self.judge.judge_code,
            judge=self.judge,
            from_date=self.today,
        )
        self.case_type = CaseTypeT.objects.create(
            case_type=1,
            type_name="WP",
            type_flag="C",
            est_code_src="ASK001",
            reg_no=0,
            reg_year=int(self.today.year),
        )

    def test_resolve_by_bench_code_returns_config_with_matching_key(self):
        cfg = resolve_bench_for_registration("REG01")
        self.assertEqual(cfg.bench_key, "REG01")
        self.assertEqual(cfg.bench_code, "REG01")

    def test_resolve_by_bench_key_alias_matches_bench_code(self):
        cfg = resolve_bench_for_registration("REG01")
        self.assertEqual(cfg.bench_key, "REG01")

    def test_unknown_bench_raises(self):
        with self.assertRaises(ValueError):
            resolve_bench_for_registration("NO_SUCH_BENCH")

    @override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
    def test_finalize_persists_bench_key(self):
        ef = Efiling.objects.create(
            is_draft=False,
            status="UNDER_SCRUTINY",
            case_type=self.case_type,
            created_by=self.user,
        )
        pdf = SimpleUploadedFile("p.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        doc = EfilingDocuments.objects.create(
            e_filing=ef,
            e_filing_number=ef.e_filing_number,
            document_type="PETITION",
            final_document=pdf,
        )
        EfilingDocumentsIndex.objects.create(
            document=doc,
            document_part_name="PETITION",
            file_part_path="efile/x/p.pdf",
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )
        out = finalize_approved_filing(ef, user=self.user, bench="REG01")
        self.assertEqual(out.bench, "REG01")
        self.assertTrue(out.case_number)

    @override_settings(EFILING_VALIDATE_PDF_UPLOAD=False)
    def test_finalize_rejects_bad_bench(self):
        ef = Efiling.objects.create(
            is_draft=False,
            status="UNDER_SCRUTINY",
            case_type=self.case_type,
            created_by=self.user,
        )
        pdf = SimpleUploadedFile("p2.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        doc = EfilingDocuments.objects.create(
            e_filing=ef,
            e_filing_number=ef.e_filing_number,
            document_type="PETITION",
            final_document=pdf,
        )
        EfilingDocumentsIndex.objects.create(
            document=doc,
            document_part_name="PETITION",
            file_part_path="efile/z/p.pdf",
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )
        with self.assertRaises(ValidationError):
            finalize_approved_filing(ef, user=self.user, bench="INVALID")
