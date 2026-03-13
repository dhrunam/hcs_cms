from django.test import SimpleTestCase

from apps.core.models import State


class StateModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(State._meta.db_table, "state")

    def test_field_exists(self):
        self.assertEqual(State._meta.get_field("state").name, "state")
