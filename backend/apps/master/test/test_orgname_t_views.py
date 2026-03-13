from django.test import SimpleTestCase
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import OrgnameT
from apps.master.serializers.orgname_t_serializers import OrgnameTSerializer
from apps.master.views.orgname_t_views import OrgnameTListView


class OrgnameTListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(OrgnameTListView.serializer_class, OrgnameTSerializer)

    def test_queryset_model(self):
        self.assertEqual(OrgnameTListView.queryset.model, OrgnameT)

    def test_permission_classes(self):
        self.assertEqual(OrgnameTListView.permission_classes, [IsAuthenticatedOrReadOnly])
