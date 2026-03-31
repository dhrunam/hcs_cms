from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'
    label = 'core'

    def ready(self) -> None:
        # Register signal handlers (file deletion, etc).
        import apps.core.signals  # noqa: F401
