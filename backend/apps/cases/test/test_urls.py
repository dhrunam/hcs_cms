from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.cases import urls as cases_urls


class CasesUrlsTest(SimpleTestCase):
    def test_cases_router_contains_api_root_only(self):
        route_names = {pattern.name for pattern in cases_urls.urlpatterns}
        self.assertEqual(route_names, {"api-root"})

    def test_cases_api_root_url(self):
        url = reverse("cases:api-root")
        self.assertEqual(url, "/api/v1/cases/")
        self.assertEqual(resolve(url).url_name, "api-root")
