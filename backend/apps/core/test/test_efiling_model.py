from django.test import SimpleTestCase

from apps.core.models import CaseTypeT, Efiling


class EfilingModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(Efiling._meta.db_table, "e_filing")

    def test_case_type_relationship(self):
        field = Efiling._meta.get_field("case_type")
        self.assertEqual(field.related_model, CaseTypeT)
