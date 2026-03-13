from django.test import SimpleTestCase

from apps.core.models import District, OrgnameT, OrgtypeT, State


class OrgnameTModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(OrgnameT._meta.db_table, "orgname_t")

    def test_foreign_keys(self):
        self.assertEqual(OrgnameT._meta.get_field("orgtype").related_model, OrgtypeT)
        self.assertEqual(OrgnameT._meta.get_field("state_id").related_model, State)
        self.assertEqual(OrgnameT._meta.get_field("district_id").related_model, District)
