"""JWT auth URL routing and token obtain (requires migrated DB)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts import roles as role_defs
from apps.accounts.tokens import primary_role_key_for_user


class JwtAuthRoutingTests(TestCase):
    def test_token_obtain_url(self):
        url = reverse("accounts:token_obtain_pair")
        self.assertEqual(url, "/api/v1/accounts/auth/token/")

    def test_register_party_url(self):
        url = reverse("accounts:register_party")
        self.assertEqual(url, "/api/v1/accounts/auth/register/party/")


class JwtTokenClaimsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="claimstest",
            email="claims@test.invalid",
            password="test-pass-123",
            first_name="",
            last_name="",
        )
        g, _ = Group.objects.get_or_create(name=role_defs.GROUP_ADVOCATE)
        self.user.groups.add(g)

    def test_primary_role_key_for_user(self):
        self.assertEqual(primary_role_key_for_user(self.user), role_defs.ROLE_ADVOCATE)


class JwtTokenObtainByPhoneTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="phone_login_user",
            email="phone_login@test.invalid",
            password="test-pass-Phone9",
            first_name="",
            last_name="",
            phone_number="9876543210",
        )

    def test_obtain_token_with_phone_in_email_field(self):
        client = APIClient()
        url = reverse("accounts:token_obtain_pair")
        res = client.post(
            url,
            {"email": "9876543210", "password": "test-pass-Phone9"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)

    def test_unknown_phone_returns_400(self):
        client = APIClient()
        url = reverse("accounts:token_obtain_pair")
        res = client.post(
            url,
            {"email": "1111111111", "password": "test-pass-Phone9"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
