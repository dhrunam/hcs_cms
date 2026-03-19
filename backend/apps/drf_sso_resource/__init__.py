"""
drf-sso-resource
================
A reusable Django app that turns any DRF project into an OAuth2/OIDC
resource server.

Quick-start
-----------
1. Add 'drf_sso_resource' to INSTALLED_APPS.
2. Set SSO_INTROSPECTION_URL, SSO_CLIENT_ID, SSO_CLIENT_SECRET in settings.
3. Use SSOResourceServerAuthentication in DEFAULT_AUTHENTICATION_CLASSES.

See conf.py for the full list of supported settings and their defaults.
"""

__version__ = "1.0.0"
__all__ = [
    "SSOResourceServerAuthentication",
]


def __getattr__(name):
    if name == "SSOResourceServerAuthentication":
        from .authentication import SSOResourceServerAuthentication

        return SSOResourceServerAuthentication
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
