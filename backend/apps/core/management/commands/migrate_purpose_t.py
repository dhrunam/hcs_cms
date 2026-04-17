from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, transaction

from apps.cis import legacy_models
from apps.core.models import PurposeT


class Command(BaseCommand):
    help = "Migrate PurposeT rows from the CIS legacy database into the core database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Read and map records without committing database changes",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete existing PurposeT rows before migration",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of legacy rows processed",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        truncate = options["truncate"]
        limit = options["limit"]

        counts = {"created": 0, "updated": 0, "skipped": 0}
        queryset = legacy_models.PurposeT.objects.using("cis_legacy").all().order_by("purpose_code")
        if limit is not None:
            queryset = queryset[:limit]

        self.stdout.write(self.style.NOTICE("Starting PurposeT migration from cis_legacy to core."))

        try:
            with transaction.atomic():
                if truncate:
                    deleted_count, _ = PurposeT.objects.all().delete()
                    self.stdout.write(self.style.WARNING(f"Deleted {deleted_count} existing PurposeT rows."))

                for row in queryset.iterator(chunk_size=1000):
                    if row.purpose_code is None:
                        counts["skipped"] += 1
                        continue

                    defaults = {
                        "purpose_name": row.purpose_name,
                        "lpurpose_name": row.lpurpose_name,
                        "purpose_flag": row.purpose_flag,
                        "display": row.display or "",
                        "purpose_priority": row.purpose_priority,
                        "res_disp": row.res_disp,
                        "national_code": row.national_code,
                        "substage_id": row.substage_id,
                        "amd": row.amd,
                        "create_modify": row.create_modify,
                        "est_code_src": row.est_code_src,
                        "is_active": True,
                    }

                    _, created = PurposeT.objects.update_or_create(
                        purpose_code=row.purpose_code,
                        defaults=defaults,
                    )
                    if created:
                        counts["created"] += 1
                    else:
                        counts["updated"] += 1

                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("Dry run enabled. Rolling back changes."))
        except OperationalError as exc:
            raise CommandError(
                "Unable to connect to the current or legacy database. "
                "Verify the default and cis_legacy database settings, then retry. "
                f"Original error: {exc}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "PurposeT migration finished: "
                f"created={counts['created']}, updated={counts['updated']}, skipped={counts['skipped']}"
            )
        )