"""SimpleJWT serializers with HCS user checks (claims come from HCSAccessToken)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenBlacklistSerializer,
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from apps.accounts.tokens import HCSRefreshToken


class HCSTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = HCSRefreshToken

    def _normalize_login_identifier(self, attrs: dict) -> dict:
        """
        The JSON field name stays ``email`` (USERNAME_FIELD), but the value may be
        either an email address or a phone number that matches ``User.phone_number``.
        """
        User = get_user_model()
        field = self.username_field
        raw = (attrs.get(field) or "").strip()
        if not raw:
            raise serializers.ValidationError({field: "This field may not be blank."})

        if "@" in raw:
            attrs[field] = raw
            return attrs

        qs = User.objects.filter(phone_number__iexact=raw)
        count = qs.count()
        if count > 1:
            raise serializers.ValidationError(
                {
                    "detail": "Multiple accounts use this phone number. Sign in with your email address."
                }
            )
        user = qs.first()
        if user is None:
            raise serializers.ValidationError(
                {"detail": "No account found with this phone number."}
            )
        attrs[field] = user.email
        return attrs

    def validate(self, attrs):
        attrs = self._normalize_login_identifier(attrs)
        User = get_user_model()
        field = self.username_field
        login_value = (attrs.get(field) or "").strip()
        password = attrs.get("password")
        if login_value and password:
            try:
                candidate = User.objects.get(**{field: login_value})
            except User.DoesNotExist:
                candidate = None
            if (
                candidate is not None
                and candidate.check_password(password)
                and not candidate.is_active
            ):
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Your account is inactive. Sign-in requires activation by an administrator "
                            "after your identity documents are verified. Please contact the court office "
                            "if you need assistance."
                        )
                    },
                    code="account_inactive",
                )

        data = super().validate(attrs)
        user = self.user
        if getattr(settings, "REGISTRATION_REQUIRE_EMAIL_VERIFICATION", False):
            reg = getattr(user, "registration_type", None) or ""
            if reg in (
                "party_in_person",
                "advocate",
            ) and not getattr(user, "email_verified", True):
                raise serializers.ValidationError(
                    {"detail": "Email address is not verified yet."},
                    code="email_not_verified",
                )
        return data


class HCSTokenRefreshSerializer(TokenRefreshSerializer):
    token_class = HCSRefreshToken


class HCSTokenBlacklistSerializer(TokenBlacklistSerializer):
    token_class = HCSRefreshToken
