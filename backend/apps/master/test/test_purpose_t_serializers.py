from django.test import SimpleTestCase

from apps.core.models import PurposeT
from apps.master.serializers.purpose_t_serializers import PurposeTSerializer


class PurposeTSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(PurposeTSerializer.Meta.model, PurposeT)

    def test_meta_fields(self):
        self.assertEqual(PurposeTSerializer.Meta.fields, "__all__")