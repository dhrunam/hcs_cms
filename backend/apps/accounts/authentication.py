from __future__ import annotations

from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


class SSOIntrospectionAuthentication(BaseAuthentication):
    """Validate external SSO bearer tokens via introspection endpoint."""

    www_authenticate_realm = "api"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        try:
            token = auth[1].decode("utf-8")
        except UnicodeError as exc:
            raise exceptions.AuthenticationFailed("Invalid bearer token.") from exc

        claims = self._introspect_token(token)
        if not claims.get("active", False):
            raise exceptions.AuthenticationFailed("Invalid or expired access token.")

        user = self._get_or_create_user(claims)
        return user, None

    def authenticate_header(self, request):
        return f'Bearer realm="{self.www_authenticate_realm}"'

    def _introspect_token(self, token: str) -> dict[str, Any]:
        introspection_url = settings.SSO_INTROSPECTION_URL
        if not introspection_url:
            raise exceptions.AuthenticationFailed("SSO introspection is not configured.")

        try:
            response = requests.post(
                introspection_url,
                data={"token": token},
                auth=(settings.SSO_CLIENT_ID, settings.SSO_CLIENT_SECRET)
                if settings.SSO_CLIENT_ID and settings.SSO_CLIENT_SECRET
                else None,
                timeout=5,
                verify=settings.SSO_VERIFY_SSL,
            )
        except requests.RequestException as exc:
            raise exceptions.AuthenticationFailed(
                "Unable to connect to SSO introspection service."
            ) from exc

        if response.status_code >= 400:
            raise exceptions.AuthenticationFailed(
                "Unable to validate access token with SSO provider."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise exceptions.AuthenticationFailed(
                "Invalid response from SSO introspection service."
            ) from exc

        return payload

    def _get_or_create_user(self, claims: dict[str, Any]):
        user_model = get_user_model()

        sub = str(claims.get("sub") or "").strip()
        email = str(claims.get("email") or "").strip().lower()
        preferred_username = str(
            claims.get("preferred_username") or claims.get("username") or ""
        ).strip()
        first_name = str(claims.get("given_name") or "").strip()
        last_name = str(claims.get("family_name") or "").strip()

        username_seed = preferred_username or (email.split("@")[0] if email else sub)
        if not username_seed:
            raise exceptions.AuthenticationFailed("Token does not include usable identity claims.")

        if email:
            user = user_model.objects.filter(email=email).first()
        else:
            username_exact = username_seed[:150]
            user = user_model.objects.filter(username=username_exact).first()

        if not user:
            username = self._next_available_username(user_model, username_seed)
            resolved_email = email or self._next_available_email(user_model, username, sub)
            user = user_model(
                username=username,
                email=resolved_email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
            user.set_unusable_password()
            user.save()
            return user

        updated = False
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if email and user.email != email:
            user.email = email
            updated = True

        if updated:
            user.save(update_fields=["first_name", "last_name", "email"])

        return user

    def _next_available_username(self, user_model, seed: str) -> str:
        base = (seed or "user")[:150]
        candidate = base
        suffix = 1

        while user_model.objects.filter(username=candidate).exists():
            suffix_text = f"-{suffix}"
            candidate = f"{base[:150 - len(suffix_text)]}{suffix_text}"
            suffix += 1

        return candidate

    def _next_available_email(self, user_model, username: str, sub: str) -> str:
        local_part = (sub or username or "user").replace("@", "_")
        local_part = local_part[:50] if len(local_part) > 50 else local_part

        candidate = f"{local_part}@sso.local"
        suffix = 1

        while user_model.objects.filter(email=candidate).exists():
            candidate = f"{local_part}-{suffix}@sso.local"
            suffix += 1

        return candidate
