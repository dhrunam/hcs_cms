from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.cis import urls as cis_urls


class CisUrlsTest(SimpleTestCase):
    def test_cis_router_contains_api_root_only(self):
        route_names = {pattern.name for pattern in cis_urls.urlpatterns}
        self.assertEqual(route_names, {"api-root"})

    def test_cis_api_root_url(self):
        url = reverse("cis:api-root")
        self.assertEqual(url, "/api/v1/cis/")
        self.assertEqual(resolve(url).url_name, "api-root")
