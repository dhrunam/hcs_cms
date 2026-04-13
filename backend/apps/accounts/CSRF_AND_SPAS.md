# CSRF and Angular + Django (JWT)

This API uses **Bearer JWT** in the `Authorization` header (SimpleJWT **refresh** tokens are sent in JSON bodies, not cookies).

- Browser-based CSRF primarily targets **cookie-authenticated** requests. Third-party sites cannot attach your `Authorization` header automatically, so the classic CSRF pattern does not apply to header-only JWT calls.
- Keep **refresh tokens out of cookies** unless you also implement `SameSite`, `Secure`, and CSRF protection on refresh routes (plan option B).

Hybrid note: `SessionAuthentication` + cookies would require `X-CSRFToken` on unsafe methods; JWT-only API views do not use session auth for Bearer requests.
