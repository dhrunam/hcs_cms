from django.test import SimpleTestCase

from apps.core.models import CivilT


class CivilTModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(CivilT._meta.db_table, "civil_t")

    def test_key_fields_exist(self):
        self.assertEqual(CivilT._meta.get_field("cino").name, "cino")
        self.assertEqual(CivilT._meta.get_field("hashkey").name, "hashkey")
