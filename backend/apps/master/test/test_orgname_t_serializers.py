from django.test import SimpleTestCase

from apps.core.models import OrgnameT
from apps.master.serializers.orgname_t_serializers import OrgnameTSerializer


class OrgnameTSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(OrgnameTSerializer.Meta.model, OrgnameT)

    def test_meta_fields(self):
        self.assertEqual(OrgnameTSerializer.Meta.fields, "__all__")
