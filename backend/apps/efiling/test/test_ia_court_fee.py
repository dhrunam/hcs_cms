from django.conf import settings
from django.test import TestCase

from apps.core.models import CaseTypeT, Efiling, EfilingDocuments, IA
from apps.efiling.ia_court_fee import ia_court_fee_payment_satisfied
from apps.payment.models import PaymentTransaction


class IaCourtFeeSatisfiedTest(TestCase):
    def setUp(self):
        self.case_type = CaseTypeT.objects.create(
            case_type=1,
            type_name="WP",
            type_flag="C",
            est_code_src="ASK001",
            reg_no=0,
            reg_year=0,
        )
        self.filing = Efiling.objects.create(
            case_type=self.case_type,
            petitioner_name="P",
            petitioner_contact="9876543210",
            bench="Principal Bench",
            is_draft=False,
        )
        self.ia = IA.objects.create(
            e_filing=self.filing,
            e_filing_number=self.filing.e_filing_number,
            ia_text="relief",
            status="DRAFT",
        )
        self.doc = EfilingDocuments.objects.create(
            e_filing=self.filing,
            e_filing_number=self.filing.e_filing_number,
            document_type="IA",
            is_ia=True,
            ia_number=self.ia.ia_number,
        )
        self.payment_status = getattr(
            settings,
            "PG_PAYMENT_STATUS",
            {"initiated": "initiated", "success": "success", "failed": "failed"},
        )
        self.success = self.payment_status.get("success", "success")

    def test_legacy_ia_fee_ref_satisfies(self):
        PaymentTransaction.objects.create(
            payment_type="IA Court Fee",
            payment_mode="online",
            application=f"IA-FEE-{self.ia.id}",
            reference_no="LEG-1",
            status=self.success,
            amount="10",
            court_fees="10",
            callback_payload={},
        )
        self.assertTrue(ia_court_fee_payment_satisfied(self.ia.id))

    def test_ia_filing_flow_with_efiling_application_satisfies(self):
        PaymentTransaction.objects.create(
            payment_type="application",
            payment_mode="online",
            application=str(self.filing.id),
            reference_no="NEW-1",
            status=self.success,
            amount="10",
            court_fees="10",
            callback_payload={
                "source": "ia_filing",
                "efiling_document_id": self.doc.id,
            },
        )
        self.assertTrue(ia_court_fee_payment_satisfied(self.ia.id))

    def test_ia_filing_wrong_document_ia_number_does_not_satisfy(self):
        other_doc = EfilingDocuments.objects.create(
            e_filing=self.filing,
            e_filing_number=self.filing.e_filing_number,
            document_type="IA",
            is_ia=True,
            ia_number="IA20999999999",
        )
        PaymentTransaction.objects.create(
            payment_type="application",
            payment_mode="online",
            application=str(self.filing.id),
            reference_no="NEW-2",
            status=self.success,
            amount="10",
            court_fees="10",
            callback_payload={
                "source": "ia_filing",
                "efiling_document_id": other_doc.id,
            },
        )
        self.assertFalse(ia_court_fee_payment_satisfied(self.ia.id))
