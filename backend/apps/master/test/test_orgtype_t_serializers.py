from django.test import SimpleTestCase

from apps.core.models import OrgtypeT
from apps.master.serializers.orgtype_t_serializers import OrgtypeTSerializer


class OrgtypeTSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(OrgtypeTSerializer.Meta.model, OrgtypeT)

    def test_meta_fields(self):
        self.assertEqual(OrgtypeTSerializer.Meta.fields, "__all__")
