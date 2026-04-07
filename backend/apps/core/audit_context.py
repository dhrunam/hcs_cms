from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Iterator

from django.contrib.auth.models import AnonymousUser


_current_user: ContextVar[object | None] = ContextVar("current_audit_user", default=None)


def _normalize_user(user: object | None) -> object | None:
    if user is None or isinstance(user, AnonymousUser):
        return None
    if getattr(user, "is_authenticated", False):
        return user
    return None


def set_current_user(user: object | None) -> Token:
    return _current_user.set(_normalize_user(user))


def get_current_user() -> object | None:
    return _current_user.get()


def reset_current_user(token: Token) -> None:
    _current_user.reset(token)


@contextmanager
def audit_user_context(user: object | None) -> Iterator[object | None]:
    token = set_current_user(user)
    try:
        yield get_current_user()
    finally:
        reset_current_user(token)