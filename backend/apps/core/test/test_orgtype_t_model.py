from django.test import SimpleTestCase

from apps.core.models import OrgtypeT


class OrgtypeTModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(OrgtypeT._meta.db_table, "orgtype_t")

    def test_field_exists(self):
        self.assertEqual(OrgtypeT._meta.get_field("orgtype").name, "orgtype")
