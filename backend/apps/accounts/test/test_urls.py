from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.accounts.views import UserViewSet


class AccountsUrlsTest(SimpleTestCase):
    def test_user_list_url(self):
        url = reverse("accounts:user-list")
        self.assertEqual(url, "/api/v1/accounts/users/")
        self.assertEqual(resolve(url).func.cls, UserViewSet)

    def test_user_detail_url(self):
        url = reverse("accounts:user-detail", kwargs={"pk": 1})
        self.assertEqual(url, "/api/v1/accounts/users/1/")
        self.assertEqual(resolve(url).func.cls, UserViewSet)

    def test_user_me_action_url(self):
        url = reverse("accounts:user-me")
        self.assertEqual(url, "/api/v1/accounts/users/me/")
        self.assertEqual(resolve(url).func.cls, UserViewSet)
