from django.test import SimpleTestCase

from apps.core.models import Court
from apps.master.serializers.court_serializers import CourtSerializer


class CourtSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(CourtSerializer.Meta.model, Court)

    def test_meta_fields(self):
        self.assertEqual(CourtSerializer.Meta.fields, "__all__")
