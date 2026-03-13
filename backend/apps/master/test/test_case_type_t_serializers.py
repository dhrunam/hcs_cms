from django.test import SimpleTestCase

from apps.core.models import CaseTypeT
from apps.master.serializers.case_type_t_serializers import CaseTypeTSerializer


class CaseTypeTSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(CaseTypeTSerializer.Meta.model, CaseTypeT)

    def test_meta_fields(self):
        self.assertEqual(CaseTypeTSerializer.Meta.fields, "__all__")
