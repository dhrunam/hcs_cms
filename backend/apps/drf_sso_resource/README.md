# drf-sso-resource

Reusable Django REST Framework authentication app for OAuth2/OIDC resource servers.

## Features

- Bearer token validation via OAuth2 introspection
- Optional userinfo fallback when identity claims are incomplete
- Pluggable user sync handler
- Token/introspection caching support
- Scope and role permission helpers

---

## Installation

### From PyPI (once published)

```bash
pip install drf-sso-resource
```

### From a local wheel (development / internal use)

Build the wheel from the package directory first:

```bash
cd path/to/drf_sso_resource
pip install build
python -m build
```

Then install the generated wheel into your project's virtual environment:

```bash
pip install path/to/drf_sso_resource/dist/drf_sso_resource-1.0.0-py3-none-any.whl
```

### From source (editable, for active development)

```bash
pip install -e path/to/drf_sso_resource
```

---

## Quick-start guide for a new project

### 1. Add to `INSTALLED_APPS`

```python
# settings.py
INSTALLED_APPS = [
    ...
    "drf_sso_resource",
]
```

### 2. Run migrations

The package ships one migration that creates the `SSOUserProfile` table:

```bash
python manage.py migrate drf_sso_resource
```

### 3. Configure SSO settings

Add the following to your `settings.py`. The first three are required; the
rest are optional overrides with sensible defaults (see [All settings](#all-settings)):

```python
# ── Required ──────────────────────────────────────────────────────────────
SSO_INTROSPECTION_URL = "https://sso.example.com/o/introspect/"
SSO_CLIENT_ID         = "my-resource-server-client-id"
SSO_CLIENT_SECRET     = env("SSO_CLIENT_SECRET")   # load from environment

# ── Optional (shown with their defaults) ──────────────────────────────────
SSO_ENABLE_USERINFO_FALLBACK = True      # fetch /userinfo/ when sub is missing
SSO_INTROSPECTION_CACHE_TTL  = 120       # seconds; capped at token expiry
SSO_HTTP_TIMEOUT             = 3         # per-request timeout in seconds

# Permission gate behavior (used by AdminEditorOrReadOnly)
SSO_PERMISSION_WRITE_GROUPS = ("API_WRITERS", "API_ADMINS")
SSO_PERMISSION_WRITE_ROLES = ("admin", "editor")
SSO_PERMISSION_ALLOW_STAFF = True
SSO_PERMISSION_ALLOW_SUPERUSER = True
```

### 4. Set the DRF authentication class

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "drf_sso_resource.authentication.SSOResourceServerAuthentication",
    ],
    # Keep IsAuthenticated only if you want the whole API private by default.
    # For mixed public/private APIs, set per-view permission classes instead.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}
```

### 5. Protect individual views (optional)

Use the bundled scope / role permission helpers for fine-grained access control:

```python
from drf_sso_resource.permissions import HasAllScopes, HasSSORole

class ArticleCreateView(APIView):
    authentication_classes = [SSOResourceServerAuthentication]
    permission_classes = [HasAllScopes]
    required_scopes = ["cms:write"]   # all scopes must be present

class AdminDashboardView(APIView):
    permission_classes = [HasSSORole]
    required_roles = ["admin"]        # user must belong to the mapped Django group
```

---

## All settings

| Setting | Default | Description |
|---|---|---|
| `SSO_INTROSPECTION_URL` | `None` *(required)* | Token introspection endpoint URL |
| `SSO_CLIENT_ID` | `None` *(required)* | OAuth2 client ID of this resource server |
| `SSO_CLIENT_SECRET` | `None` *(required)* | OAuth2 client secret — keep in environment |
| `SSO_USER_SYNC_HANDLER` | `"drf_sso_resource.user_sync.map_sso_user"` | Dotted path to `callable(sso_id, username, email, claims) → User` |
| `SSO_USER_PROFILE_MODEL` | `"drf_sso_resource.SSOUserProfile"` | Swappable profile model (`app_label.Model`) |
| `SSO_AUTO_PROVISION_USER` | `False` | Auto-create users not found locally |
| `SSO_ENABLE_USERINFO_FALLBACK` | `True` | Fetch `/userinfo/` when introspection lacks identity claims |
| `OAUTH2_USERINFO_URL` | derived from `OAUTH2_SERVER_URL` | Explicit userinfo endpoint URL |
| `SSO_INTROSPECTION_CACHE_TTL` | `120` | Introspection result cache TTL in seconds |
| `SSO_USERINFO_CACHE_TTL` | `300` | Userinfo result cache TTL in seconds |
| `SSO_HTTP_TIMEOUT` | `3` | HTTP request timeout in seconds |
| `SSO_HTTP_RETRY_TOTAL` | `1` | Total retry attempts for failed HTTP calls |
| `SSO_SIGNAL_AUTO_SYNC` | `True` | Connect `app_authorized` signal handler automatically |
| `SSO_SUB_CLAIM_KEYS` | `("sub", "id")` | Claim keys searched for the subject identifier |
| `SSO_USERNAME_CLAIM_KEYS` | `("preferred_username", "username", "email")` | Claim keys searched for the username |
| `SSO_SCOPE_GROUP_PREFIX` | `"SSO_SCOPE_"` | Prefix for scope-derived Django groups |
| `SSO_CLAIM_GROUP_KEYS` | `("groups", "roles")` | Claim keys to read group membership from |
| `SCOPE_TO_GROUP_MAP` | `{}` | Optional explicit map: OAuth2 scope value → Django group name |
| `SCOPE_TO_PERMISSION_MAP` | built-in defaults | Maps OAuth2 scope → Django permission codenames |
| `ROLE_TO_GROUP_MAP` | built-in defaults | Maps OIDC role value → Django group name |
| `SSO_PERMISSION_ALLOW_SAFE_METHODS` | `True` | If `True`, configured safe methods are read-public in `AdminEditorOrReadOnly` |
| `SSO_PERMISSION_SAFE_METHODS` | `("GET", "HEAD", "OPTIONS")` | Methods treated as safe for read access |
| `SSO_PERMISSION_WRITE_GROUPS` | `("API_WRITERS", "API_ADMINS")` | Django groups allowed write access |
| `SSO_PERMISSION_WRITE_ROLES` | `("admin", "editor")` | Role values on user object allowed write access |
| `SSO_PERMISSION_USER_ROLES_ATTR` | `"roles"` | User attribute name containing role values |
| `SSO_PERMISSION_ALLOW_STAFF` | `True` | Allow `is_staff` users to write |
| `SSO_PERMISSION_ALLOW_SUPERUSER` | `True` | Allow `is_superuser` users to write |

---

## Custom user sync handler

Replace the default handler by pointing `SSO_USER_SYNC_HANDLER` at your own callable:

```python
# myapp/sso_sync.py
def my_sync(sso_id, username, email, claims):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=username, defaults={"email": email or ""})
    # ... custom logic (assign groups, update profile, etc.)
    return user
```

```python
# settings.py
SSO_USER_SYNC_HANDLER = "myapp.sso_sync.my_sync"
```

---

## How authentication works

1. The `Authorization: Bearer <token>` header is extracted from the request.
2. The token is introspected against `SSO_INTROSPECTION_URL` (result cached by SHA-256 digest).
3. If introspection returns `active: false` or fails:
   - **Safe methods** (GET, HEAD, OPTIONS) → treated as anonymous (allows public read endpoints).
   - **Write methods** (POST, PUT, PATCH, DELETE) → `401 Unauthorized`.
4. If `sub` (subject identifier) is missing from the introspection response, `/userinfo/` is consulted as a fallback (requires `SSO_ENABLE_USERINFO_FALLBACK = True`).
5. If `sub` is present but no username claim is found, a deterministic fallback username is derived from the `sub` value (`sso_<sha256[:24]>`). Only a completely missing `sub` triggers a `401`.
6. `SSO_USER_SYNC_HANDLER` is called to get or create the local User record.
7. `request.sso_claims` and `request.token_scopes` are attached for use in views and permission classes.

---

## Requirements

- Python ≥ 3.11
- Django ≥ 4.2
- djangorestframework ≥ 3.14
- requests ≥ 2.28
