from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.efiling.views.efiling_acts_views import EfilingActsListCreateView, EfilingActsRetrieveUpdateDestroyView
from apps.efiling.views.efiling_case_details_views import EfilingCaseDetailsListCreateView, EfilingCaseDetailsRetrieveUpdateDestroyView
from apps.efiling.views.efiling_litigant_views import EfilingLitigantListCreateView, EfilingLitigantRetrieveUpdateDestroyView
from apps.efiling.views.efiling_views import EfilingListCreateView, EfilingRetrieveUpdateDestroyView
from apps.efiling.views.ia_views import IAListCreateView, IARetrieveUpdateDestroyView


class EfilingUrlsTest(SimpleTestCase):
    def test_efiling_list_create_url(self):
        url = reverse("efiling:efiling-list-create")
        self.assertEqual(url, "/api/v1/efiling/efilings/")
        self.assertEqual(resolve(url).func.view_class, EfilingListCreateView)

    def test_efiling_detail_url(self):
        url = reverse("efiling:efiling-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/efiling/efilings/1/")
        self.assertEqual(resolve(url).func.view_class, EfilingRetrieveUpdateDestroyView)

    def test_ia_list_create_url(self):
        url = reverse("efiling:ia-list-create")
        self.assertEqual(url, "/api/v1/efiling/ias/")
        self.assertEqual(resolve(url).func.view_class, IAListCreateView)

    def test_ia_detail_url(self):
        url = reverse("efiling:ia-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/efiling/ias/1/")
        self.assertEqual(resolve(url).func.view_class, IARetrieveUpdateDestroyView)

    def test_efiling_litigant_list_create_url(self):
        url = reverse("efiling:efiling-litigant-list-create")
        self.assertEqual(url, "/api/v1/efiling/efiling-litigants/")
        self.assertEqual(resolve(url).func.view_class, EfilingLitigantListCreateView)

    def test_efiling_litigant_detail_url(self):
        url = reverse("efiling:efiling-litigant-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/efiling/efiling-litigants/1/")
        self.assertEqual(resolve(url).func.view_class, EfilingLitigantRetrieveUpdateDestroyView)

    def test_efiling_case_details_list_create_url(self):
        url = reverse("efiling:efiling-case-details-list-create")
        self.assertEqual(url, "/api/v1/efiling/efiling-case-details/")
        self.assertEqual(resolve(url).func.view_class, EfilingCaseDetailsListCreateView)

    def test_efiling_case_details_detail_url(self):
        url = reverse("efiling:efiling-case-details-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/efiling/efiling-case-details/1/")
        self.assertEqual(resolve(url).func.view_class, EfilingCaseDetailsRetrieveUpdateDestroyView)

    def test_efiling_acts_list_create_url(self):
        url = reverse("efiling:efiling-acts-list-create")
        self.assertEqual(url, "/api/v1/efiling/efiling-acts/")
        self.assertEqual(resolve(url).func.view_class, EfilingActsListCreateView)

    def test_efiling_acts_detail_url(self):
        url = reverse("efiling:efiling-acts-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/efiling/efiling-acts/1/")
        self.assertEqual(resolve(url).func.view_class, EfilingActsRetrieveUpdateDestroyView)
