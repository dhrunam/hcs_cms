from django.test import SimpleTestCase

from apps.core.models import OrgtypeT
from apps.master.serializers.orgtype_t_serializers import OrgtypeTSerializer
from apps.master.views.orgtype_t_views import OrgtypeTListView


class OrgtypeTListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(OrgtypeTListView.serializer_class, OrgtypeTSerializer)

    def test_queryset_model(self):
        self.assertEqual(OrgtypeTListView.queryset.model, OrgtypeT)
