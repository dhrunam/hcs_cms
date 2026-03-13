from django.test import SimpleTestCase
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import CaseTypeT
from apps.master.serializers.case_type_t_serializers import CaseTypeTSerializer
from apps.master.views.case_type_t_views import CaseTypeTListView


class CaseTypeTListViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(CaseTypeTListView.serializer_class, CaseTypeTSerializer)

    def test_queryset_model(self):
        self.assertEqual(CaseTypeTListView.queryset.model, CaseTypeT)

    def test_permission_classes(self):
        self.assertEqual(CaseTypeTListView.permission_classes, [IsAuthenticatedOrReadOnly])
