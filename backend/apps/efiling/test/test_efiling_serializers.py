from django.test import SimpleTestCase, TestCase

from apps.core.models import CaseTypeT, Efiling, EfilingActs, EfilingCaseDetails, EfilingLitigant
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer
from apps.efiling.serializers.efiling_serializers import EfilingCaseTypeSerializer, EfilingSerializer


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
            "is_draft",
            "status",
            "accepted_at",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        self.assertEqual(EfilingSerializer.Meta.fields, expected_fields)

    def test_read_only_fields(self):
        self.assertEqual(EfilingSerializer.Meta.read_only_fields, ["id", "created_at", "updated_at"])


class EfilingSerializerRepresentationTest(TestCase):
    def test_case_type_is_serialized_as_nested_object(self):
        case_type = CaseTypeT.objects.create(
            case_type=101,
            type_name="Original Application",
            full_form="Original Application Full Form",
            type_flag="A",
            est_code_src="ASK001",
        )
        efiling = Efiling.objects.create(
            case_type=case_type,
            bench="Principal Bench",
        )

        serialized_data = EfilingSerializer(instance=efiling).data

        self.assertEqual(
            serialized_data["case_type"],
            EfilingCaseTypeSerializer(case_type).data,
        )

    def test_case_type_input_still_accepts_primary_key(self):
        case_type = CaseTypeT.objects.create(
            case_type=102,
            type_name="Appeal",
            full_form="Appeal Full Form",
            type_flag="A",
            est_code_src="ASK001",
        )
        serializer = EfilingSerializer(
            data={
                "case_type": case_type.pk,
                "bench": "Circuit Bench",
                "petitioner_name": "Sample Petitioner",
                "petitioner_contact": "9876543210",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["case_type"], case_type)


class EfilingLitigantSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingLitigantSerializer.Meta.model, EfilingLitigant)

    def test_serializer_includes_new_fields(self):
        self.assertIn("organization", EfilingLitigantSerializer.Meta.fields)
        self.assertIn("sequence_number", EfilingLitigantSerializer.Meta.fields)


class EfilingCaseDetailsSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingCaseDetailsSerializer.Meta.model, EfilingCaseDetails)


class EfilingActsSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingActsSerializer.Meta.model, EfilingActs)
