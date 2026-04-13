"""Thin wrappers around SimpleJWT views with shared throttling."""

from __future__ import annotations

from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.accounts.throttling import AuthTokenThrottle


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [AuthTokenThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [AuthTokenThrottle]


class ThrottledTokenVerifyView(TokenVerifyView):
    throttle_classes = [AuthTokenThrottle]


class ThrottledTokenBlacklistView(TokenBlacklistView):
    throttle_classes = [AuthTokenThrottle]
