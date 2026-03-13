from django.test import SimpleTestCase

from apps.core.models import BaseModel


class BaseModelTest(SimpleTestCase):
    def test_base_model_is_abstract(self):
        self.assertTrue(BaseModel._meta.abstract)

    def test_base_model_common_fields_exist(self):
        expected = {"created_at", "updated_at", "created_by", "updated_by", "is_active"}
        self.assertTrue(expected.issubset({field.name for field in BaseModel._meta.fields}))
