from django.test import SimpleTestCase

from apps.core.models import Court


class CourtModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(Court._meta.db_table, "court")

    def test_required_field_exists(self):
        self.assertEqual(Court._meta.get_field("est_code_src").name, "est_code_src")
