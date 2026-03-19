from unittest.mock import patch

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import exceptions
from rest_framework.test import APIRequestFactory

from drf_sso_resource.authentication import SSOResourceServerAuthentication
from drf_sso_resource.permissions import AdminEditorOrReadOnly, HasAllScopes, HasAnyScope
from drf_sso_resource.user_sync import map_sso_user


class SSOResourceServerAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = SSOResourceServerAuthentication()
        self.user = get_user_model().objects.create_user(
            username="sso_tester", email="sso_tester@example.com", password="x"
        )

    def test_authenticate_returns_none_without_bearer_header(self):
        request = self.factory.get("/api/cms/events/")
        self.assertIsNone(self.auth.authenticate(request))

    def test_authenticate_rejects_malformed_bearer_header(self):
        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer token with spaces",
        )
        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch.object(SSOResourceServerAuthentication, "_sync_user")
    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_success_sets_claims_on_request(self, mock_introspect, mock_sync):
        mock_introspect.return_value = {
            "active": True,
            "sub": "sub-123",
            "preferred_username": "sso_tester",
            "email": "sso_tester@example.com",
            "scope": "api:read api:write",
        }
        mock_sync.return_value = self.user

        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )

        user, token = self.auth.authenticate(request)
        self.assertEqual(user.pk, self.user.pk)
        self.assertEqual(token.token, "valid-token")
        self.assertEqual(request.token_scopes, ["api:read", "api:write"])
        self.assertEqual(request.sso_claims["sub"], "sub-123")

    @patch.object(SSOResourceServerAuthentication, "_sync_user")
    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_derives_username_when_only_sub_present(self, mock_introspect, mock_sync):
        mock_introspect.return_value = {
            "active": True,
            "sub": "sub-only-123",
            "scope": "api:read",
        }
        mock_sync.return_value = self.user

        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )
        user, _ = self.auth.authenticate(request)

        self.assertEqual(user.pk, self.user.pk)
        self.assertTrue(mock_sync.called)
        _sso_id, derived_username, _email, _claims = mock_sync.call_args[0]
        self.assertEqual(_sso_id, "sub-only-123")
        self.assertTrue(str(derived_username).startswith("sso_"))

    @patch.object(SSOResourceServerAuthentication, "_sync_user")
    @patch.object(SSOResourceServerAuthentication, "_userinfo")
    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_uses_userinfo_fallback(self, mock_introspect, mock_userinfo, mock_sync):
        mock_introspect.return_value = {
            "active": True,
            "scope": "api:read",
        }
        mock_userinfo.return_value = {
            "sub": "u-1",
            "preferred_username": "fallback_user",
            "email": "fallback@example.com",
        }
        mock_sync.return_value = self.user

        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer valid-token",
        )
        user, _ = self.auth.authenticate(request)
        self.assertEqual(user.pk, self.user.pk)
        mock_userinfo.assert_called_once_with("valid-token")

    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_returns_none_for_inactive_token_on_safe_method(self, mock_introspect):
        mock_introspect.return_value = None
        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer bad-token",
        )
        self.assertIsNone(self.auth.authenticate(request))

    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_fails_when_token_is_inactive_on_write_method(self, mock_introspect):
        mock_introspect.return_value = None
        request = self.factory.post(
            "/api/cms/events/",
            {},
            format="json",
            HTTP_AUTHORIZATION="Bearer bad-token",
        )
        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch.object(SSOResourceServerAuthentication, "_userinfo")
    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_fails_if_identity_claims_missing(self, mock_introspect, mock_userinfo):
        mock_introspect.return_value = {
            "active": True,
            "scope": "api:read",
        }
        mock_userinfo.return_value = {}
        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer token-no-identity",
        )
        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch.object(SSOResourceServerAuthentication, "_sync_user")
    @patch.object(SSOResourceServerAuthentication, "_introspect")
    def test_authenticate_fails_when_sync_handler_returns_none(self, mock_introspect, mock_sync):
        mock_introspect.return_value = {
            "active": True,
            "sub": "sub-1",
            "preferred_username": "user-a",
            "email": "user-a@example.com",
            "scope": "api:read",
        }
        mock_sync.return_value = None
        request = self.factory.get(
            "/api/cms/events/",
            HTTP_AUTHORIZATION="Bearer token",
        )
        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch("drf_sso_resource.authentication._HTTP_SESSION.post")
    @patch("drf_sso_resource.authentication.cache.get")
    def test_introspect_uses_cached_value(self, mock_cache_get, mock_post):
        mock_cache_get.return_value = {"active": True, "sub": "cached"}
        result = self.auth._introspect("cached-token")
        self.assertEqual(result.get("sub"), "cached")
        mock_post.assert_not_called()

    @patch("drf_sso_resource.authentication._HTTP_SESSION.post")
    @patch("drf_sso_resource.authentication.cache.get")
    def test_introspect_returns_none_on_non_200_response(self, mock_cache_get, mock_post):
        mock_cache_get.return_value = None
        mock_resp = type("Resp", (), {"status_code": 500, "json": lambda self: {}})()
        mock_post.return_value = mock_resp
        result = self.auth._introspect("bad-status-token")
        self.assertIsNone(result)


class ScopePermissionTests(TestCase):
    def setUp(self):
        self.any_scope = HasAnyScope()
        self.all_scope = HasAllScopes()

    def test_has_any_scope_allows_if_one_scope_matches(self):
        request = type("Req", (), {"token_scopes": ["cms:read", "cms:publish"]})()
        view = type("View", (), {"required_scopes": ["cms:write", "cms:publish"]})()
        self.assertTrue(self.any_scope.has_permission(request, view))

    def test_has_all_scopes_requires_full_subset(self):
        request = type("Req", (), {"token_scopes": ["cms:read"]})()
        view = type("View", (), {"required_scopes": ["cms:read", "cms:write"]})()
        self.assertFalse(self.all_scope.has_permission(request, view))


class AdminEditorOrReadOnlySettingsTests(TestCase):
    def setUp(self):
        self.permission = AdminEditorOrReadOnly()
        self.user = get_user_model().objects.create_user(
            username="writer_user", email="writer@example.com", password="x"
        )

    @staticmethod
    def _make_request(method, user):
        return type("Req", (), {"method": method, "user": user})()

    @override_settings(SSO_PERMISSION_WRITE_GROUPS=("CMS_WRITERS",))
    def test_write_allowed_for_configured_group(self):
        group = Group.objects.create(name="CMS_WRITERS")
        self.user.groups.add(group)
        request = self._make_request("POST", self.user)
        self.assertTrue(self.permission.has_permission(request, object()))

    @override_settings(
        SSO_PERMISSION_WRITE_GROUPS=(),
        SSO_PERMISSION_WRITE_ROLES=("editor",),
        SSO_PERMISSION_USER_ROLES_ATTR="roles",
        SSO_PERMISSION_ALLOW_STAFF=False,
        SSO_PERMISSION_ALLOW_SUPERUSER=False,
    )
    def test_write_allowed_for_configured_role(self):
        self.user.roles = ["editor"]
        request = self._make_request("PATCH", self.user)
        self.assertTrue(self.permission.has_permission(request, object()))

    @override_settings(
        SSO_PERMISSION_ALLOW_SAFE_METHODS=False,
        SSO_PERMISSION_SAFE_METHODS=("GET", "HEAD", "OPTIONS"),
    )
    def test_safe_methods_can_be_disabled(self):
        anon_request = self._make_request("GET", None)
        self.assertFalse(self.permission.has_permission(anon_request, object()))

    @override_settings(
        SSO_PERMISSION_WRITE_GROUPS=(),
        SSO_PERMISSION_WRITE_ROLES=(),
        SSO_PERMISSION_ALLOW_STAFF=False,
        SSO_PERMISSION_ALLOW_SUPERUSER=False,
    )
    def test_write_denied_when_no_grant_path_exists(self):
        request = self._make_request("POST", self.user)
        self.assertFalse(self.permission.has_permission(request, object()))

    @override_settings(
        SSO_PERMISSION_WRITE_GROUPS="CMS_WRITERS, CMS_ADMINS",
        SSO_PERMISSION_WRITE_ROLES="editor admin",
        SSO_PERMISSION_USER_ROLES_ATTR="roles",
    )
    def test_string_settings_are_parsed_for_groups_and_roles(self):
        self.user.roles = ["editor"]
        request = self._make_request("PUT", self.user)
        self.assertTrue(self.permission.has_permission(request, object()))


class UserSyncMappingTests(TestCase):
    @override_settings(
        ROLE_TO_GROUP_MAP={
            "admin": "API_ADMINS",
            "editor": "API_WRITERS",
            "viewer": "API_READERS",
        },
        SCOPE_TO_GROUP_MAP={
            "api:read": "API_READERS",
            "api:write": "API_WRITERS",
        },
        SSO_SCOPE_GROUP_PREFIX="SSO_SCOPE_",
    )
    def test_map_sso_user_applies_role_and_scope_group_mappings(self):
        claims = {
            "roles": ["editor"],
            "scope": "api:read api:write",
        }

        user = map_sso_user(
            sso_id="sub-1001",
            username="mapped_user",
            email="mapped_user@example.com",
            claims=claims,
        )

        groups = set(user.groups.values_list("name", flat=True))
        self.assertIn("API_WRITERS", groups)
        self.assertIn("API_READERS", groups)

        # Existing prefixed scope-group behavior remains active.
        self.assertIn("SSO_SCOPE_API:READ", groups)
        self.assertIn("SSO_SCOPE_API:WRITE", groups)

    @override_settings(
        ROLE_TO_GROUP_MAP={"admin": "API_ADMINS"},
    )
    def test_map_sso_user_maps_role_name_to_group_name(self):
        claims = {
            "roles": ["admin"],
        }

        user = map_sso_user(
            sso_id="sub-2001",
            username="admin_user",
            email="admin_user@example.com",
            claims=claims,
        )

        groups = set(user.groups.values_list("name", flat=True))
        self.assertIn("API_ADMINS", groups)

    @override_settings(
        ROLE_TO_GROUP_MAP={
            "editor": "API_WRITERS",
        },
    )
    def test_map_sso_user_reapplies_groups_when_claims_unchanged(self):
        claims = {
            "roles": ["editor"],
        }

        user = map_sso_user(
            sso_id="sub-3001",
            username="repeat_user",
            email="repeat_user@example.com",
            claims=claims,
        )

        self.assertTrue(user.groups.filter(name="API_WRITERS").exists())

        # Simulate membership drift between logins.
        user.groups.remove(*Group.objects.filter(name="API_WRITERS"))
        self.assertFalse(user.groups.filter(name="API_WRITERS").exists())

        # Same claims again should restore mapped groups.
        user = map_sso_user(
            sso_id="sub-3001",
            username="repeat_user",
            email="repeat_user@example.com",
            claims=claims,
        )
        self.assertTrue(user.groups.filter(name="API_WRITERS").exists())