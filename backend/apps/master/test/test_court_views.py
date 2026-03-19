from django.test import SimpleTestCase

from apps.core.models import Court
from apps.master.serializers.court_serializers import CourtSerializer
from apps.master.views.court_views import CourtListView


class CourtListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(CourtListView.serializer_class, CourtSerializer)

    def test_queryset_model(self):
        self.assertEqual(CourtListView.queryset.model, Court)
