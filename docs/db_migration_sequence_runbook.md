# DB Migration and Sequence Runbook

## Purpose
Prevent and recover from PostgreSQL sequence desynchronization errors such as:
`duplicate key value violates unique constraint "django_migrations_pkey"`.

## Normal deployment steps
1. Run `python manage.py migrate`.
2. Verify with `python manage.py showmigrations`.
3. Start services.

## After DB restore/clone
Run sequence resync once before migrations:

```sql
SELECT setval(
  pg_get_serial_sequence('django_migrations', 'id'),
  COALESCE((SELECT MAX(id) FROM django_migrations), 1),
  true
);
```

## If migration fails with duplicate key on django_migrations
1. Resync sequence using SQL above.
2. Re-run `python manage.py migrate`.

## If migration partially created tables and then failed
1. Check whether expected tables already exist.
2. If objects exist and schema matches migration, run:
   `python manage.py migrate <app> <target_migration> --fake`
3. Re-run `python manage.py showmigrations <app>` and verify `[X]`.

## Do not
- Do not manually insert rows into `django_migrations`.
- Do not manually assign integer PK values in application code.
