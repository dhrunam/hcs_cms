from django.test import SimpleTestCase, TestCase

from apps.core.models import (
    CaseTypeT,
    District,
    Efiling,
    EfilingActs,
    EfilingCaseDetails,
    EfilingLitigant,
    OrgnameT,
    State,
)
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer
from apps.efiling.serializers.efiling_litigant_serializers import (
    EfilingDistrictSerializer,
    EfilingLitigantSerializer,
    EfilingOrganizationSerializer,
    EfilingStateSerializer,
)
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
            "case_number",
            "is_draft",
            "status",
            "accepted_at",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "petitioner_vs_respondent",
        ]
        self.assertEqual(EfilingSerializer.Meta.fields, expected_fields)

    def test_read_only_fields(self):
        self.assertEqual(
            EfilingSerializer.Meta.read_only_fields,
            [
                "id",
                "e_filing_number",
                "case_number",
                "status",
                "accepted_at",
                "created_at",
                "updated_at",
                "petitioner_vs_respondent",
            ],
        )


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
        self.assertIn("organization_detail", EfilingLitigantSerializer.Meta.fields)
        self.assertIn("state_detail", EfilingLitigantSerializer.Meta.fields)
        self.assertIn("district_detail", EfilingLitigantSerializer.Meta.fields)


class EfilingLitigantSerializerRepresentationTest(TestCase):
    def setUp(self):
        self.state = State.objects.create(state="Maharashtra", est_code_src="ASK001")
        self.district = District.objects.create(state_id=self.state, district="Mumbai")
        self.organization = OrgnameT.objects.create(
            orgname="ABC Organization",
            state_id=self.state,
            district_id=self.district,
            taluka_code=1,
            village_code=1,
            village1_code=1,
            village2_code=1,
            town_code=1,
            ward_code=1,
            est_code_src="ASK001",
        )
        self.efiling = Efiling.objects.create(bench="Principal Bench")

    def test_get_response_contains_detail_objects_with_names(self):
        litigant = EfilingLitigant.objects.create(
            e_filing=self.efiling,
            e_filing_number=self.efiling.e_filing_number,
            organization=self.organization,
            sequence_number=1,
            name="Test Petitioner",
            state_id=self.state,
            district_id=self.district,
        )

        serialized_data = EfilingLitigantSerializer(instance=litigant).data

        self.assertEqual(serialized_data["organization"], self.organization.pk)
        self.assertEqual(serialized_data["state_id"], self.state.pk)
        self.assertEqual(serialized_data["district_id"], self.district.pk)
        self.assertEqual(
            serialized_data["organization_detail"],
            EfilingOrganizationSerializer(self.organization).data,
        )
        self.assertEqual(
            serialized_data["state_detail"],
            EfilingStateSerializer(self.state).data,
        )
        self.assertEqual(
            serialized_data["district_detail"],
            EfilingDistrictSerializer(self.district).data,
        )

    def test_get_response_returns_null_details_when_relations_missing(self):
        litigant = EfilingLitigant.objects.create(
            e_filing=self.efiling,
            e_filing_number=self.efiling.e_filing_number,
            sequence_number=2,
            name="Test Respondent",
        )

        serialized_data = EfilingLitigantSerializer(instance=litigant).data

        self.assertIsNone(serialized_data["organization_detail"])
        self.assertIsNone(serialized_data["state_detail"])
        self.assertIsNone(serialized_data["district_detail"])

    def test_input_still_accepts_ids_for_create_update(self):
        serializer = EfilingLitigantSerializer(
            data={
                "e_filing": self.efiling.pk,
                "e_filing_number": self.efiling.e_filing_number,
                "organization": self.organization.pk,
                "sequence_number": 3,
                "name": "Input Validation Litigant",
                "state_id": self.state.pk,
                "district_id": self.district.pk,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["organization"], self.organization)
        self.assertEqual(serializer.validated_data["state_id"], self.state)
        self.assertEqual(serializer.validated_data["district_id"], self.district)


class EfilingCaseDetailsSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingCaseDetailsSerializer.Meta.model, EfilingCaseDetails)


class EfilingActsSerializerTest(SimpleTestCase):
    def test_serializer_meta_model(self):
        self.assertEqual(EfilingActsSerializer.Meta.model, EfilingActs)
