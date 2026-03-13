from django.test import SimpleTestCase

from apps.core.models import CaseTypeT


class CaseTypeTModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(CaseTypeT._meta.db_table, "case_type_t")

    def test_required_field_exists(self):
        self.assertEqual(CaseTypeT._meta.get_field("case_type").name, "case_type")
