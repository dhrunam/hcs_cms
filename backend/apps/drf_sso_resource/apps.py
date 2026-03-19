from django.apps import AppConfig


class DRFSSOResourceConfig(AppConfig):
    name = "drf_sso_resource"
    verbose_name = "DRF SSO Resource Server"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Connect the app_authorized signal handler so every project that
        # has SSO_SIGNAL_AUTO_SYNC = True gets user syncing for free.
        from . import signals  # noqa: F401
