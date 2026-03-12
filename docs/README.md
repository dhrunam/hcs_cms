# HCS CMS – High Court of Sikkim Case Management System

A **monolithic-repository** web application for managing court cases at the High Court of Sikkim.

| Layer | Technology | Port |
|-------|-----------|------|
| Frontend | Angular 21 (public OAuth2 client) | 4200 |
| Backend API | Django 6 + Django REST Framework (confidential OAuth2 client + resource server) | 8000 |
| OAuth2 / SSO | Django OAuth Toolkit (embedded in the backend) | 8000 |
| Database | PostgreSQL 16 | 5432 |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser / Client                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │  HTTP
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│          Angular 21 Frontend  (PUBLIC OAuth2 client)            │
│  • Authorization Code flow + PKCE                               │
│  • angular-oauth2-oidc  •  Angular Material  •  Port 4200       │
└────────────────────────────┬────────────────────────────────────┘
                             │  REST API  +  Bearer token
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│     Django 6 Backend  (CONFIDENTIAL OAuth2 client + server)     │
│  ┌─────────────────────────┐  ┌───────────────────────────────┐ │
│  │  Django REST Framework  │  │   Django OAuth Toolkit        │ │
│  │  /api/v1/               │  │   /o/  (Authorization Server) │ │
│  │  • cases                │  │   • /authorize/               │ │
│  │  • accounts             │  │   • /token/                   │ │
│  └─────────────────────────┘  │   • /userinfo/                │ │
│                               │   • /revoke_token/            │ │
│                               └───────────────────────────────┘ │
│  Port 8000                                                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │  SQL
                              ▼
                  ┌─────────────────────┐
                  │   PostgreSQL 16      │
                  │   Port 5432          │
                  └─────────────────────┘
```

### OAuth2 / SSO Flow

```
Angular (public client)                 Django Backend (Authorization Server)
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
       │──── GET /api/v1/cases/                       │
       │     Authorization: Bearer <access_token> ───▶│
       │◀──── 200 { cases: [...] } ───────────────────│
```

---

## Project Structure

```
hcs_cms/
├── backend/                    # Django DRF + OAuth2 server
│   ├── apps/
│   │   ├── accounts/           # Custom User model + API
│   │   └── cases/              # Case management API
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
- **Backend API**: http://localhost:8000/api/v1/
- **Admin panel**: http://localhost:8000/admin/
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
python manage.py runserver 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start                          # http://localhost:4200
```

---

## Registering the Angular App as an OAuth2 Client

1. Go to **http://localhost:8000/admin/** → **Django OAuth Toolkit → Applications → Add Application**
2. Fill in:
   - **Client id**: `hcs-cms-frontend`
   - **Client type**: `Public`
   - **Authorization grant type**: `Authorization code`
   - **Redirect URIs**: `http://localhost:4200/auth/callback`
   - **Algorithm**: `RS256` (or `HS256`)
3. Save. The frontend will use PKCE so no client secret is needed.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cases/` | List cases |
| POST | `/api/v1/cases/` | Create case |
| GET | `/api/v1/cases/{id}/` | Get case detail |
| PUT/PATCH | `/api/v1/cases/{id}/` | Update case |
| DELETE | `/api/v1/cases/{id}/` | Delete case |
| GET | `/api/v1/accounts/users/` | List users |
| GET | `/api/v1/accounts/users/me/` | Current user profile |
| POST | `/o/token/` | Get / refresh token |
| POST | `/o/revoke_token/` | Revoke token |
| GET | `/o/userinfo/` | OIDC user info |

All `/api/v1/` endpoints require a valid Bearer token.

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
