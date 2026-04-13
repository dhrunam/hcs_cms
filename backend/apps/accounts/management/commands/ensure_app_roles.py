"""Create Django Groups for all application roles (idempotent)."""

from __future__ import annotations

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts import roles as role_defs


class Command(BaseCommand):
    help = "Ensure Django auth Groups exist for ROLE_TO_GROUP_MAP (safe to re-run)."

    def handle(self, *args, **options):
        created = 0
        for name in role_defs.ALL_GROUP_NAMES:
            _, was_created = Group.objects.get_or_create(name=name)
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created group: {name}"))
        if created == 0:
            self.stdout.write("All role groups already exist.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. Created {created} group(s)."))
