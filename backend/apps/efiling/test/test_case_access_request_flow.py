from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.core.models import (
    CaseAccessRequest,
    Efiling,
    EfilingDocuments,
    EfilingDocumentsIndex,
)
from apps.efiling.views.case_access_request_views import CaseAccessRequestReviewView


class CaseAccessRequestApprovalFlowTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.review_view = CaseAccessRequestReviewView.as_view()

        scrutiny_group, _ = Group.objects.get_or_create(name="SCRUTINY_OFFICER")
        self.scrutiny_officer = User.objects.create_user(
            username="scrutiny-user",
            email="scrutiny@example.com",
            password="password123",
        )
        self.scrutiny_officer.groups.add(scrutiny_group)

        self.case_owner = User.objects.create_user(
            username="case-owner",
            email="owner@example.com",
            password="password123",
        )
        self.advocate_a = User.objects.create_user(
            username="adv-a",
            email="adv-a@example.com",
            password="password123",
            first_name="Arjun",
            last_name="Sharma",
        )
        self.advocate_b = User.objects.create_user(
            username="adv-b",
            email="adv-b@example.com",
            password="password123",
            first_name="Priya",
            last_name="Verma",
        )

        self.filing = Efiling.objects.create(
            e_filing_number="ASK20240000003C202400003",
            case_number="WP(C)/11/2024",
            petitioner_name="Test Petitioner",
            is_draft=False,
            status="ACCEPTED",
            created_by=self.case_owner,
            updated_by=self.case_owner,
        )

    def _create_request(self, advocate: User, filename: str) -> CaseAccessRequest:
        pdf = SimpleUploadedFile(
            filename,
            b"%PDF-1.4\n% test vakalatnama\n",
            content_type="application/pdf",
        )
        return CaseAccessRequest.objects.create(
            advocate=advocate,
            e_filing=self.filing,
            case_number=self.filing.case_number,
            vakalatnama_document=pdf,
            status=CaseAccessRequest.Status.PENDING,
        )

    def _approve_request(self, req: CaseAccessRequest):
        request = self.factory.patch(
            f"/api/v1/efiling/case-access-requests/{req.id}/review/",
            {"status": "APPROVED"},
            format="json",
        )
        force_authenticate(request, user=self.scrutiny_officer)
        return self.review_view(request, pk=req.id)

    def test_approved_access_request_appends_indexed_vakalatnama_with_advocate_name(self):
        EfilingDocumentsIndex.objects.create(
            document=EfilingDocuments.objects.create(
                e_filing=self.filing,
                e_filing_number=self.filing.e_filing_number,
                document_type="AFFIDAVIT",
            ),
            document_part_name="Affidavit",
            document_sequence=1,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )
        vakalat_anchor = EfilingDocumentsIndex.objects.create(
            document=EfilingDocuments.objects.create(
                e_filing=self.filing,
                e_filing_number=self.filing.e_filing_number,
                document_type="VAKALATNAMA",
            ),
            document_part_name="Vakalatnama (Original)",
            document_sequence=3,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )
        EfilingDocumentsIndex.objects.create(
            document=EfilingDocuments.objects.create(
                e_filing=self.filing,
                e_filing_number=self.filing.e_filing_number,
                document_type="ANNEXURE",
            ),
            document_part_name="Annexure",
            document_sequence=9,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )

        req_a = self._create_request(self.advocate_a, "vakalatnama-a.pdf")
        req_b = self._create_request(self.advocate_b, "vakalatnama-b.pdf")

        resp_a = self._approve_request(req_a)
        resp_b = self._approve_request(req_b)
        self.assertEqual(resp_a.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_b.status_code, status.HTTP_200_OK)

        added_rows = (
            EfilingDocumentsIndex.objects.filter(
                document__e_filing=self.filing,
                document__document_type="VAKALATNAMA",
                document_part_name__startswith="Vakalatnama - ",
            )
            .order_by("id")
        )
        self.assertEqual(added_rows.count(), 2)
        self.assertEqual(
            [x.document_part_name for x in added_rows],
            ["Vakalatnama - Arjun Sharma", "Vakalatnama - Priya Verma"],
        )
        self.assertTrue(all(x.document_sequence == 3 for x in added_rows))
        self.assertTrue(all(x.parent_document_index_id == vakalat_anchor.id for x in added_rows))
        self.assertTrue(all(x.scrutiny_status == EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED for x in added_rows))
        self.assertTrue(all(x.is_new_for_scrutiny is False for x in added_rows))
        self.assertTrue(all(x.is_compliant is True for x in added_rows))

        unaffected = EfilingDocumentsIndex.objects.filter(
            document__e_filing=self.filing,
            document_part_name="Annexure",
        ).first()
        self.assertIsNotNone(unaffected)
        self.assertEqual(unaffected.document_sequence, 9)

    def test_approved_access_request_uses_next_sequence_when_no_vakalat_anchor_exists(self):
        EfilingDocumentsIndex.objects.create(
            document=EfilingDocuments.objects.create(
                e_filing=self.filing,
                e_filing_number=self.filing.e_filing_number,
                document_type="PETITION",
            ),
            document_part_name="Petition Main",
            document_sequence=2,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )
        EfilingDocumentsIndex.objects.create(
            document=EfilingDocuments.objects.create(
                e_filing=self.filing,
                e_filing_number=self.filing.e_filing_number,
                document_type="AFFIDAVIT",
            ),
            document_part_name="Affidavit",
            document_sequence=7,
            scrutiny_status=EfilingDocumentsIndex.ScrutinyStatus.ACCEPTED,
            is_compliant=True,
        )

        req = self._create_request(self.advocate_a, "vakalatnama-fallback.pdf")
        response = self._approve_request(req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        added_row = EfilingDocumentsIndex.objects.filter(
            document__e_filing=self.filing,
            document_part_name="Vakalatnama - Arjun Sharma",
        ).first()
        self.assertIsNotNone(added_row)
        self.assertEqual(added_row.document_sequence, 8)
        self.assertIsNone(added_row.parent_document_index_id)
