from __future__ import annotations

from django.apps import AppConfig


class JudgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.judge"
    label = "judge"

    def ready(self) -> None:
        # Wire signal handlers only. Avoid any DB queries at app startup because
        # database connectivity may be unavailable when runserver boots.
        from . import signals  # noqa: F401

