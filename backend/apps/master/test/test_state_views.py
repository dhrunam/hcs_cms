from django.test import SimpleTestCase

from apps.core.models import State
from apps.master.serializers.state_serializers import StateSerializer
from apps.master.views.state_views import StateListView


class StateListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(StateListView.serializer_class, StateSerializer)

    def test_queryset_model(self):
        self.assertEqual(StateListView.queryset.model, State)
