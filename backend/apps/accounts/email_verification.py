"""Signed tokens for optional email verification (no third-party dependency)."""

from __future__ import annotations

from django.core import signing

SIGN_SALT = "hcs.accounts.email_verify"


def make_email_verification_token(user_id: int) -> str:
    return signing.dumps({"uid": user_id}, salt=SIGN_SALT)


def load_email_verification_token(token: str, max_age: int = 7 * 86400) -> int | None:
    try:
        data = signing.loads(token, salt=SIGN_SALT, max_age=max_age)
        return int(data["uid"])
    except (signing.BadSignature, signing.SignatureExpired, KeyError, ValueError, TypeError):
        return None
