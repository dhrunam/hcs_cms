"""DRF throttle scopes for registration and auth endpoints."""

from __future__ import annotations

from rest_framework.throttling import AnonRateThrottle


class RegistrationThrottle(AnonRateThrottle):
    scope = "registration"


class AuthTokenThrottle(AnonRateThrottle):
    scope = "auth"
