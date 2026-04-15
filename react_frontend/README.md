# HCS CMS React Frontend

Production-oriented React + TypeScript frontend scaffold mapped from the Angular project domains.

## Tech Stack

- React 19 + TypeScript
- Vite 8
- React Router
- Axios
- Vitest + React Testing Library + MSW
- ESLint + Type-aware TypeScript config

## Run

```bash
npm install
npm run dev
```

Build:

```bash
npm run build
npm run preview
```

Test:

```bash
npm run test
```

## Environment

Copy and edit `.env.example`:

```bash
cp .env.example .env
```

Variables:

- `VITE_API_BASE_URL` (default: `http://localhost:8000/api/v1`)

## Project Structure

```text
src/
  app/
    providers/
    routes/
  features/
    auth/
      api/
      components/
      pages/
    advocate/
    party/
    scrutiny-officers/
    listing-officers/
    judges/
    reader/
    steno/
    common/
  shared/
    components/
    layouts/
    lib/
    types/
```

## Route Mapping (Angular parity)

Public:

- `/auth/redirect`
- `/user/login`
- `/user/register`
- `/user/register/party`
- `/user/register/advocate`
- `/user/verify-email`

Protected role areas:

- `/party-in-person`
- `/advocate`
- `/scrutiny-officers`
- `/listing-officers`
- `/judges`
- `/reader`
- `/steno`

Each role area now includes nested child routes (for example, `/advocate/filings`, `/judges/board`) and is loaded lazily.

## API Notes

Current scaffold expects DRF-compatible accounts endpoints:

- `POST /accounts/auth/token/`
- `POST /accounts/auth/token/refresh/`
- `GET /accounts/users/me`
- `POST /accounts/auth/register/party/`
- `POST /accounts/auth/register/advocate/`
- `POST /accounts/auth/verify-email/`

The React app stores access token + refresh token + session user in localStorage, performs silent token refresh on 401 (single retry), and guards private routes by role.

## Next Implementation Steps

1. Add API error normalization and user-facing toast notifications.
2. Add MSW integration tests for registration and refresh retry scenarios.
3. Expand role modules with real domain components from Angular feature parity.
