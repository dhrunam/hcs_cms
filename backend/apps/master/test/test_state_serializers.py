from django.test import SimpleTestCase

from apps.core.models import State
from apps.master.serializers.state_serializers import StateSerializer


class StateSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(StateSerializer.Meta.model, State)

    def test_meta_fields(self):
        self.assertEqual(StateSerializer.Meta.fields, "__all__")
