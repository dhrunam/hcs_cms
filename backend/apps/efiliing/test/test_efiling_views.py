from django.test import SimpleTestCase

from apps.core.models import Efiling
from apps.efiliing.serializers.efiling_serializers import EfilingSerializer
from apps.efiliing.views.efiling_views import EfilingListCreateView, EfilingRetrieveUpdateDestroyView


class EfilingListCreateViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(EfilingListCreateView.serializer_class, EfilingSerializer)

    def test_queryset_model(self):
        self.assertEqual(EfilingListCreateView.queryset.model, Efiling)


class EfilingRetrieveUpdateDestroyViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(EfilingRetrieveUpdateDestroyView.serializer_class, EfilingSerializer)

    def test_queryset_model(self):
        self.assertEqual(EfilingRetrieveUpdateDestroyView.queryset.model, Efiling)
