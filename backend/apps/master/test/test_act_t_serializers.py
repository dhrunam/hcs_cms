from django.test import SimpleTestCase

from apps.core.models import ActT
from apps.master.serializers.act_t_serializers import ActTSerializer


class ActTSerializerTest(SimpleTestCase):
    def test_meta_model(self):
        self.assertEqual(ActTSerializer.Meta.model, ActT)

    def test_meta_fields(self):
        self.assertEqual(ActTSerializer.Meta.fields, "__all__")
