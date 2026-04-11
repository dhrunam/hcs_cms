"""Shared helpers for registration and verification."""

from __future__ import annotations

import re

from django.contrib.auth import get_user_model


def generate_unique_username_from_email(email: str) -> str:
    """Derive a unique username from the email local part (User still requires username)."""
    User = get_user_model()
    local = (email or "").split("@", 1)[0].strip()
    base = re.sub(r"[^a-zA-Z0-9_]", "_", local)[:100] or "user"
    candidate = base
    n = 0
    while User.objects.filter(username=candidate).exists():
        n += 1
        candidate = f"{base}_{n}"
    return candidate
