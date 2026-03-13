from django.test import SimpleTestCase

from apps.core.models import District
from apps.master.serializers.district_serializers import DistrictSerializer


class DistrictSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(DistrictSerializer.Meta.model, District)

    def test_meta_fields(self):
        self.assertEqual(DistrictSerializer.Meta.fields, "__all__")
