# HCS CMS – High Court of Sikkim Case Management System

A **monolithic-repository** web application for managing court cases at the High Court of Sikkim.

| Layer | Technology | Port |
|-------|-----------|------|
| Frontend | Angular 21 | 4200 |
| Backend API | Django 6 + Django REST Framework | 8002 (dev example) |
| OAuth2 / SSO | External OIDC/OAuth2 service (`hcs_sso_with_oidc`) | 8000 |
| Database | PostgreSQL 16 | 5432 |

---

## Architecture Overview

```
Browser/Client -> Angular (4200) -> Django API (8002)
                                   |\
                                   | \-> PostgreSQL (5432)
                                   \
                                    -> External SSO/OIDC (8000) via token introspection
```

### External SSO Flow (Current)

```
Angular (public client)                 External SSO (Authorization Server)
       │                                              │
   │──── GET /o/authorize/?response_type=code ───▶│
       │         &client_id=hcs-cms-frontend           │
       │         &code_challenge=<PKCE>                │
       │◀──── 302 Redirect (login page) ──────────────│
       │                                              │
       │  User authenticates via Django admin/login   │
       │                                              │
       │◀──── 302 /auth/callback?code=<auth_code> ────│
       │                                              │
       │──── POST /o/token/ ─────────────────────────▶│
       │         code=<auth_code>                      │
       │         code_verifier=<PKCE verifier>         │
       │◀──── { access_token, id_token, ... } ────────│
       │                                              │
       │──── GET /api/v1/...                          │
       │     Authorization: Bearer <access_token> ───▶│
       │◀──── 200 { data: [...] } ────────────────────│
```

### Development Mode Note (Current)

- For active API development/testing, DRF defaults are currently open (`AllowAny`) and default authentication is disabled.
- This is temporary and should be reverted before staging/production hardening.

---

## Project Structure

```
hcs_cms/
├── backend/                    # Django DRF API
│   ├── apps/
│   │   ├── accounts/           # Custom User model + API
│   │   ├── cases/              # Cases API (router scaffold)
│   │   ├── cis/                # CIS integration scaffold
│   │   ├── core/               # Legacy mapped/core models
│   │   ├── efiling/            # Efiling CRUD APIs
│   │   └── master/             # Master data list APIs
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # Angular 21 SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/           # Auth service, interceptor, guard
│   │   │   └── features/       # Cases list, login
│   │   ├── environments/
│   │   └── styles.scss
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md

# External SSO project is maintained separately:
# hcs_sso_with_oidc/
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- PostgreSQL 16
- Docker & Docker Compose (optional, recommended)

### Option A – Docker Compose (recommended)

```bash
# Copy environment template and edit values
cp backend/.env.example backend/.env

# Start all services
docker compose up --build

# In another terminal, create a superuser
docker compose exec backend python manage.py createsuperuser
```

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8002/api/v1/
- **Admin panel**: http://localhost:8002/admin/
- **OAuth2 / SSO**: http://localhost:8000/o/

### Option B – Manual Setup

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # Edit DATABASE_URL and SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8002
```

#### Frontend

```bash
cd frontend
npm install
npm start                          # http://localhost:4200
```

---

## Registering the Angular App as an OAuth2 Client

1. Go to SSO admin **http://localhost:8000/admin/** → **Django OAuth Toolkit → Applications → Add Application**
2. Fill in:
   - **Client id**: `hcs-cms-frontend`
   - **Client type**: `Public`
   - **Authorization grant type**: `Authorization code`
   - **Redirect URIs**: `http://localhost:4200/auth/callback`
   - **Algorithm**: `RS256` (or `HS256`)
3. Save. The frontend will use PKCE so no client secret is needed.

---

## API Endpoints (Current Implemented)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/master/states/` | List states |
| GET | `/api/v1/master/districts/` | List districts |
| GET | `/api/v1/master/case-types/` | List case types |
| GET | `/api/v1/master/courts/` | List courts |
| GET | `/api/v1/master/acts/` | List acts |
| GET | `/api/v1/master/org-types/` | List organization types |
| GET | `/api/v1/master/org-names/` | List organization names |
| GET/POST | `/api/v1/efiling/efilings/` | List/create efilings |
| GET/PUT/PATCH/DELETE | `/api/v1/efiling/efilings/{id}/` | Efiling detail/update/delete |
| GET/POST | `/api/v1/efiling/efiling-litigants/` | List/create litigants |
| GET/PUT/PATCH/DELETE | `/api/v1/efiling/efiling-litigants/{id}/` | Litigant detail/update/delete |
| GET/POST | `/api/v1/efiling/efiling-case-details/` | List/create case details |
| GET/PUT/PATCH/DELETE | `/api/v1/efiling/efiling-case-details/{id}/` | Case details detail/update/delete |
| GET/POST | `/api/v1/efiling/efiling-acts/` | List/create efiling acts |
| GET/PUT/PATCH/DELETE | `/api/v1/efiling/efiling-acts/{id}/` | Efiling acts detail/update/delete |
| GET | `/api/v1/accounts/users/` | List users |
| GET | `/api/v1/accounts/users/me/` | Current user profile |

Authentication behavior depends on environment:
- Development (current): open access for CRUD testing
- Hardened environments: Bearer token validation via external SSO introspection

## Progress Snapshot (As of 13 Mar 2026)

- Core app added under backend apps and migrations stabilized.
- Efiling APIs implemented for `Efiling`, `EfilingLitigant`, `EfilingCaseDetails`, and `EfilingActs`.
- Master data list APIs implemented for case types, states, districts, courts, org types, acts, and org names.
- URL tests and serializer/view tests were added across active apps.
- External SSO token introspection integration completed with endpoint fallback support.
- Temporary development mode enabled to test CRUD APIs without authentication.

---

## Running Tests

```bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm test
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | Django secret key (required) |
| `DEBUG` | `False` | Enable Django debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DATABASE_URL` | — | PostgreSQL connection URL |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:4200` | Allowed CORS origins |
