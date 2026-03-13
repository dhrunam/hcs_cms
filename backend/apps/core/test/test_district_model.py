from django.test import SimpleTestCase

from apps.core.models import District, State


class DistrictModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(District._meta.db_table, "district")

    def test_state_relationship(self):
        field = District._meta.get_field("state_id")
        self.assertEqual(field.related_model, State)
