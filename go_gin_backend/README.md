# HCS CMS Go Backend

Gin-based migration target for the Django backend.

## Configuration

The API server reads its runtime configuration from environment variables.

Required variables:

- `PORT`: HTTP port for the Gin server
- `JWT_SECRET`: HMAC secret used by authenticated routes

Database variables:

- `DATABASE_URL`: primary application database. This is the same env var the Django backend already uses for the master app.
- `LEGACY_DATABASE_URL`: optional explicit legacy CIS database URL used for migration endpoints

Legacy CIS compatibility variables:

- `CIS_LEGACY_DB_NAME`
- `CIS_LEGACY_DB_USER`
- `CIS_LEGACY_DB_PASSWORD`
- `CIS_LEGACY_DB_HOST`
- `CIS_LEGACY_DB_PORT`

If `LEGACY_DATABASE_URL` is unset, the Go backend will build the legacy Postgres connection string from the Django-style `CIS_LEGACY_DB_*` variables.

See [.env.example](./.env.example) for the full list.

## Routes

All application routes are mounted under ` /api/v1 `.

### Health

- `GET /health`

Response:

```json
{
	"status": "ok",
	"service": "hcs-cms-go"
}
```

### Master Data

Registered under ` /api/v1/master `.

Read-only endpoints with optional auth:

- `GET /api/v1/master/case-types`
- `GET /api/v1/master/states`
- `GET /api/v1/master/acts`
- `GET /api/v1/master/org-names`

Authenticated operational endpoints:

- `GET /api/v1/master/districts?state_id=<id>`
- `GET /api/v1/master/courts?page=<n>&page_size=<n>`
- `GET /api/v1/master/org-types`

### CIS Migration

Registered under ` /api/v1/cis/migrate `.

These endpoints require a bearer token signed with `JWT_SECRET`.

- `POST /api/v1/cis/migrate/states`
- `POST /api/v1/cis/migrate/case-types`
- `POST /api/v1/cis/migrate/acts`
- `POST /api/v1/cis/migrate/all`

Query parameters:

- `limit`: optional positive integer. When provided to `states`, only that many legacy state records are processed. Invalid values currently fall back to the default behavior and are treated as unset.

Auth failure responses:

```json
{
	"detail": "authentication credentials were not provided"
}
```

```json
{
	"detail": "invalid token"
}
```

Legacy DB unavailable response:

```json
{
	"detail": "legacy cis database is not configured"
}
```

Single-entity migration response shape:

```json
{
	"detail": "states migrated successfully",
	"created": 10,
	"updated": 3,
	"skipped": 1
}
```

`case-types` and `acts` return the same summary shape with an entity-specific `detail` message.

All-entities migration response shape:

```json
{
	"detail": "all migrations completed successfully",
	"summaries": [
		{
			"entity": "states",
			"created": 10,
			"updated": 3,
			"skipped": 1
		},
		{
			"entity": "case_types",
			"created": 5,
			"updated": 0,
			"skipped": 0
		},
		{
			"entity": "acts",
			"created": 12,
			"updated": 1,
			"skipped": 0
		}
	]
}
```

Example request:

```bash
curl -X POST \
	-H "Authorization: Bearer <jwt>" \
	"http://localhost:8080/api/v1/cis/migrate/all"
```

### Accounts

Registered under ` /api/v1/accounts `.

Implemented endpoints:

- `GET /api/v1/accounts/users/me` (requires bearer token)
- `POST /api/v1/accounts/users/logout` (requires bearer token)
- `POST /api/v1/accounts/auth/token/verify/`

DRF URL-compatibility endpoints currently return `501 Not Implemented` in Go:

- `POST /api/v1/accounts/auth/token/`
- `POST /api/v1/accounts/auth/token/refresh/`
- `POST /api/v1/accounts/auth/token/blacklist/`
- `POST /api/v1/accounts/auth/register/party/`
- `POST /api/v1/accounts/auth/register/advocate/`
- `POST /api/v1/accounts/auth/verify-email/`

## Development

Useful commands:

- `make run`
- `make test`
- `make build`
- `make tidy`
