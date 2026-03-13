from django.test import SimpleTestCase

from apps.core.models import Efiling, EfilingActs, EfilingCaseDetails, EfilingLitigant
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer
from apps.efiling.serializers.efiling_serializers import EfilingSerializer


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


class EfilingLitigantSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingLitigantSerializer.Meta.model, EfilingLitigant)


class EfilingCaseDetailsSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingCaseDetailsSerializer.Meta.model, EfilingCaseDetails)


class EfilingActsSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingActsSerializer.Meta.model, EfilingActs)
