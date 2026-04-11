"""Create a staff-provisioned user with a single role (Reader, Judge, etc.)."""

from __future__ import annotations

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from apps.accounts import roles as role_defs
from apps.accounts.models import User
from apps.accounts.utils import generate_unique_username_from_email


class Command(BaseCommand):
    help = (
        "Create a user with email/password and assign one staff role "
        f"({', '.join(sorted(role_defs.STAFF_PROVISIONED_ROLE_KEYS))})."
    )

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument(
            "--role",
            type=str,
            required=True,
            choices=sorted(role_defs.STAFF_PROVISIONED_ROLE_KEYS),
            help="Role key (maps to Django Group via ROLE_TO_GROUP_MAP).",
        )
        parser.add_argument("--first-name", type=str, default="", dest="first_name")
        parser.add_argument("--last-name", type=str, default="", dest="last_name")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError(f"User with email {email!r} already exists.")

        role_key = options["role"]
        group_name = role_defs.ROLE_TO_GROUP_MAP.get(role_key)
        if not group_name:
            raise CommandError(f"Unknown role mapping for {role_key!r}")

        user = User(
            email=email,
            username=generate_unique_username_from_email(email),
            first_name=options["first_name"] or "",
            last_name=options["last_name"] or "",
            registration_type="",
            email_verified=True,
            is_active=True,
        )
        user.set_password(options["password"])
        user.save()

        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created user id={user.pk} email={user.email} role={role_key} group={group_name}"
            )
        )
