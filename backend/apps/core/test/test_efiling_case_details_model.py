from django.test import SimpleTestCase

from apps.core.models import District, Efiling, EfilingCaseDetails, State


class EfilingCaseDetailsModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(EfilingCaseDetails._meta.db_table, "e_filing_case_details")

    def test_foreign_keys(self):
        self.assertEqual(EfilingCaseDetails._meta.get_field("e_filing").related_model, Efiling)
        self.assertEqual(EfilingCaseDetails._meta.get_field("dispute_state").related_model, State)
        self.assertEqual(EfilingCaseDetails._meta.get_field("dispute_district").related_model, District)
