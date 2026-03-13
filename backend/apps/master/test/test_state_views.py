from django.test import SimpleTestCase
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import State
from apps.master.serializers.state_serializers import StateSerializer
from apps.master.views.state_views import StateListView


class StateListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(StateListView.serializer_class, StateSerializer)

    def test_queryset_model(self):
        self.assertEqual(StateListView.queryset.model, State)

    def test_permission_classes(self):
        self.assertEqual(StateListView.permission_classes, [IsAuthenticatedOrReadOnly])
