"""SimpleJWT serializers with HCS user checks (claims come from HCSAccessToken)."""

from __future__ import annotations

from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenBlacklistSerializer,
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from apps.accounts.tokens import HCSRefreshToken


class HCSTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = HCSRefreshToken

    def validate(self, attrs):
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
