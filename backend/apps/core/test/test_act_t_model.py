from django.test import SimpleTestCase

from apps.core.models import ActT


class ActTModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(ActT._meta.db_table, "act_t")

    def test_primary_key_field(self):
        self.assertEqual(ActT._meta.pk.name, "actcode")
