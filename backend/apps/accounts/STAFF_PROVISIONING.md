# Staff-provisioned roles (Reader, Judge, Scrutiny, etc.)

Self-registration only creates **Party in person** and **Advocate** accounts. All other roles are assigned by staff.

## 1. Ensure Django Groups exist

After deploy or when setting up a fresh database:

```bash
python manage.py ensure_app_roles
```

This creates the groups named in `apps.accounts.roles.ALL_GROUP_NAMES` (e.g. `READER`, `JUDGE`, `STENO`).

## 2. Create users with a staff role

```bash
python manage.py create_staff_user reader@example.com 'secure-password' --role reader --first-name Reader --last-name One
```

Valid `--role` values are the **staff-provisioned** keys in `STAFF_PROVISIONED_ROLE_KEYS`: `scrutiny_officer`, `reader`, `listing_officer`, `steno`, `judge`, `superadmin`.

## 3. Django admin

Superusers can create users in `/admin/`, assign groups, and set **Email verified** / **Registration type** as needed.

## 4. Linking judges to `JudgeT`

Court data uses `JudgeT` (`apps.core.models`) with a `user` foreign key. After creating a JWT user with the `JUDGE` group, map them to the correct `JudgeT` row (e.g. by `judge_code`) in Django admin or a one-off script so courtroom features resolve the right profile.
