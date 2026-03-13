from django.test import SimpleTestCase

from apps.core.models import Efiling, EfilingCaseDetails, EfilingLitigant, EfilingActs
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer
from apps.efiling.serializers.efiling_serializers import EfilingSerializer
from apps.efiling.views.efiling_acts_views import EfilingActsListCreateView, EfilingActsRetrieveUpdateDestroyView
from apps.efiling.views.efiling_case_details_views import EfilingCaseDetailsListCreateView, EfilingCaseDetailsRetrieveUpdateDestroyView
from apps.efiling.views.efiling_litigant_views import EfilingLitigantListCreateView, EfilingLitigantRetrieveUpdateDestroyView
from apps.efiling.views.efiling_views import EfilingListCreateView, EfilingRetrieveUpdateDestroyView


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


class EfilingLitigantViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(EfilingLitigantListCreateView.serializer_class, EfilingLitigantSerializer)
        self.assertEqual(EfilingLitigantListCreateView.queryset.model, EfilingLitigant)

    def test_detail_view(self):
        self.assertEqual(EfilingLitigantRetrieveUpdateDestroyView.serializer_class, EfilingLitigantSerializer)
        self.assertEqual(EfilingLitigantRetrieveUpdateDestroyView.queryset.model, EfilingLitigant)


class EfilingCaseDetailsViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(EfilingCaseDetailsListCreateView.serializer_class, EfilingCaseDetailsSerializer)
        self.assertEqual(EfilingCaseDetailsListCreateView.queryset.model, EfilingCaseDetails)

    def test_detail_view(self):
        self.assertEqual(EfilingCaseDetailsRetrieveUpdateDestroyView.serializer_class, EfilingCaseDetailsSerializer)
        self.assertEqual(EfilingCaseDetailsRetrieveUpdateDestroyView.queryset.model, EfilingCaseDetails)


class EfilingActsViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(EfilingActsListCreateView.serializer_class, EfilingActsSerializer)
        self.assertEqual(EfilingActsListCreateView.queryset.model, EfilingActs)

    def test_detail_view(self):
        self.assertEqual(EfilingActsRetrieveUpdateDestroyView.serializer_class, EfilingActsSerializer)
        self.assertEqual(EfilingActsRetrieveUpdateDestroyView.queryset.model, EfilingActs)
