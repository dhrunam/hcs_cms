from django.test import SimpleTestCase

from apps.core.models import District, Efiling, EfilingLitigant, State


class EfilingLitigantModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(EfilingLitigant._meta.db_table, "e_filing_litigant")

    def test_foreign_keys(self):
        self.assertEqual(EfilingLitigant._meta.get_field("e_filing").related_model, Efiling)
        self.assertEqual(EfilingLitigant._meta.get_field("state_id").related_model, State)
        self.assertEqual(EfilingLitigant._meta.get_field("district_id").related_model, District)
