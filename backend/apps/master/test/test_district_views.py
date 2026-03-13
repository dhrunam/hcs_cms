from django.test import SimpleTestCase
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import District
from apps.master.serializers.district_serializers import DistrictSerializer
from apps.master.views.district_views import DistrictListView


class DistrictListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(DistrictListView.serializer_class, DistrictSerializer)

    def test_queryset_model(self):
        self.assertEqual(DistrictListView.queryset.model, District)

    def test_permission_classes(self):
        self.assertEqual(DistrictListView.permission_classes, [IsAuthenticatedOrReadOnly])
