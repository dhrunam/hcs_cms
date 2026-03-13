from django.test import SimpleTestCase
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import ActT
from apps.master.serializers.act_t_serializers import ActTSerializer
from apps.master.views.act_t_views import ActTListView


class ActTListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(ActTListView.serializer_class, ActTSerializer)

    def test_queryset_model(self):
        self.assertEqual(ActTListView.queryset.model, ActT)

    def test_permission_classes(self):
        self.assertEqual(ActTListView.permission_classes, [IsAuthenticatedOrReadOnly])
