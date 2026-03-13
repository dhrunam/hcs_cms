from django.test import SimpleTestCase

from apps.core.models import Efiling
from apps.efiliing.serializers.efiling_serializers import EfilingSerializer


class EfilingSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingSerializer.Meta.model, Efiling)

    def test_serializer_fields(self):
        expected_fields = [
            "id",
            "case_type",
            "bench",
            "petitioner_name",
            "petitioner_contact",
            "e_filing_number",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        self.assertEqual(EfilingSerializer.Meta.fields, expected_fields)

    def test_read_only_fields(self):
        self.assertEqual(EfilingSerializer.Meta.read_only_fields, ["id", "created_at", "updated_at"])
