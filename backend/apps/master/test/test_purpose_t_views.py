from django.test import SimpleTestCase

from apps.core.models import PurposeT
from apps.master.serializers.purpose_t_serializers import PurposeTSerializer
from apps.master.views.purpose_t_views import PurposeTListView


class PurposeTListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(PurposeTListView.serializer_class, PurposeTSerializer)

    def test_queryset_model(self):
        self.assertEqual(PurposeTListView.queryset.model, PurposeT)