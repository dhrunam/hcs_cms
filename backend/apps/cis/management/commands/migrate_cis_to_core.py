from django.core.management.base import BaseCommand
from django.db import transaction

from apps.cis import legacy_models
from apps.core import models as core_models
from apps.core.models import ActT, CaseTypeT, Court, District, OrgnameT, OrgtypeT, State


class Command(BaseCommand):
    help = "Migrate required CIS legacy master/case data into core models"

    MASTER_TASKS = ["state", "district", "orgtype_t", "orgname_t", "court", "act_t", "case_type_t"]
    CASE_TASKS = ["civil_t"]
    ALL_TASKS = MASTER_TASKS + CASE_TASKS

    def add_arguments(self, parser):
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete existing data in target core tables before migration",
        )
        parser.add_argument(
            "--only",
            nargs="+",
            default=["all"],
            choices=["all", "master", "cases", "state", "district", "orgtype_t", "orgname_t", "court", "act_t", "case_type_t", "civil_t"],
            help=(
                "Run only selected migration parts. "
                "Examples: --only master, --only cases, --only state district, --only case_type_t civil_t"
            ),
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of rows read from each selected legacy table",
        )

    def handle(self, *args, **options):
        truncate = options["truncate"]
        only = options["only"]
        limit = options["limit"]

        selected_tasks = self._resolve_selected_tasks(only)
        selected_display = ", ".join(selected_tasks)

        self.stdout.write(self.style.NOTICE(f"Starting CIS -> core data migration for: {selected_display}"))

        with transaction.atomic():
            if truncate:
                self._truncate_targets(selected_tasks)

            migration_steps = {
                "state": self._migrate_state,
                "district": self._migrate_district,
                "orgtype_t": self._migrate_orgtype,
                "orgname_t": self._migrate_orgname,
                "court": self._migrate_court,
                "act_t": self._migrate_act,
                "case_type_t": self._migrate_case_type,
                "civil_t": self._migrate_civil,
            }

            summary = {}
            for key in self.ALL_TASKS:
                if key in selected_tasks:
                    summary[key] = migration_steps[key](limit=limit)

        self.stdout.write(self.style.SUCCESS("Migration completed."))
        for key, value in summary.items():
            self.stdout.write(f"  {key}: created={value['created']}, updated={value['updated']}, skipped={value['skipped']}")

    def _resolve_selected_tasks(self, only_values):
        selected = set()

        if "all" in only_values:
            return list(self.ALL_TASKS)

        if "master" in only_values:
            selected.update(self.MASTER_TASKS)

        if "cases" in only_values:
            selected.update(self.CASE_TASKS)

        for key in only_values:
            if key in self.ALL_TASKS:
                selected.add(key)

        ordered_selected = [task for task in self.ALL_TASKS if task in selected]
        if not ordered_selected:
            return list(self.ALL_TASKS)
        return ordered_selected

    def _truncate_targets(self, selected_tasks):
        self.stdout.write(self.style.WARNING("Truncating target tables..."))

        # Delete in FK-safe order while respecting selected switches.
        if "orgname_t" in selected_tasks:
            OrgnameT.objects.all().delete()
        if "district" in selected_tasks:
            District.objects.all().delete()
        if "court" in selected_tasks:
            Court.objects.all().delete()
        if "orgtype_t" in selected_tasks:
            OrgtypeT.objects.all().delete()
        if "act_t" in selected_tasks:
            ActT.objects.all().delete()
        if "civil_t" in selected_tasks:
            core_models.Efiling.objects.all().delete()
        if "case_type_t" in selected_tasks:
            CaseTypeT.objects.all().delete()
        if "state" in selected_tasks:
            State.objects.all().delete()

    def _legacy_qs(self, model_class, limit=None):
        qs = model_class.objects.using("cis_legacy").all()
        if limit is not None:
            qs = qs[:limit]
        return qs.iterator(chunk_size=1000)

    def _migrate_state(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        for row in self._legacy_qs(legacy_models.State, limit=limit):
            if not row.state_id:
                counts["skipped"] += 1
                continue

            defaults = {
                "state": row.state,
                "create_modify": row.create_modify,
                "est_code_src": (row.est_code_src or "")[:6],
            }

            # New model has CharField for national_code while legacy may be missing it in this table.
            if hasattr(row, "national_code") and row.national_code is not None:
                defaults["national_code"] = str(row.national_code)[:15]

            obj, created = State.objects.update_or_create(id=row.state_id, defaults=defaults)
            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts

    def _migrate_district(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        qs = self._legacy_qs(legacy_models.DistrictT, limit=limit)
        for row in qs:
            if not row.dist_code:
                counts["skipped"] += 1
                continue

            state_obj = State.objects.filter(id=row.state_id).first()

            defaults = {
                "state_id": state_obj,
                "district": row.dist_name,
            }
            if row.national_code is not None:
                defaults["natinal_code"] = str(row.national_code)[:15]

            # District model has implicit id PK. Use update_or_create by unique business key.
            existing = District.objects.filter(state_id=state_obj, district=row.dist_name).first()
            if existing:
                for field, value in defaults.items():
                    setattr(existing, field, value)
                existing.save(update_fields=list(defaults.keys()))
                counts["updated"] += 1
            else:
                District.objects.create(**defaults)
                counts["created"] += 1

        return counts

    def _migrate_orgtype(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        for row in self._legacy_qs(legacy_models.OrgtypeT, limit=limit):
            if row.orgcode is None:
                counts["skipped"] += 1
                continue

            defaults = {
                "orgtype": row.orgtype,
                "national_code": (row.national_code or "")[:15],
            }

            obj, created = OrgtypeT.objects.update_or_create(id=row.orgcode, defaults=defaults)
            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts

    def _migrate_orgname(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        legacy_dist_name_by_key = {
            (dist.state_id, dist.dist_code): dist.dist_name
            for dist in legacy_models.DistrictT.objects.using("cis_legacy").all().iterator(chunk_size=1000)
        }

        qs = self._legacy_qs(legacy_models.OrgnameT, limit=limit)
        for row in qs:
            if row.orgid is None:
                counts["skipped"] += 1
                continue

            orgtype_obj = OrgtypeT.objects.filter(id=row.orgtype).first()
            state_obj = State.objects.filter(id=row.state_id).first() if row.state_id is not None else None

            district_obj = None
            if row.dist_code is not None:
                district_name = legacy_dist_name_by_key.get((row.state_id, row.dist_code))
                district_qs = District.objects.filter(district=district_name)
                if state_obj:
                    district_qs = district_qs.filter(state_id=state_obj)
                district_obj = district_qs.first()

            defaults = {
                "orgtype": orgtype_obj,
                "orgname": row.orgname,
                "contactperson": row.contactperson,
                "address": row.address,
                "state_id": state_obj,
                "district_id": district_obj,
                "taluka_code": row.taluka_code or 0,
                "village_code": row.village_code or 0,
                "email": row.email,
                "mobile": row.mobile,
                "phone": row.phone,
                "fax": row.fax,
                "village1_code": row.village1_code or 0,
                "village2_code": row.village2_code or 0,
                "town_code": row.town_code or 0,
                "ward_code": row.ward_code or 0,
                "national_code": (row.national_code or "")[:15],
                "est_code_src": (row.est_code_src or "")[:6],
            }

            obj, created = OrgnameT.objects.update_or_create(id=row.orgid, defaults=defaults)
            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts

    def _migrate_court(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        qs = self._legacy_qs(legacy_models.CourtT, limit=limit)
        for row in qs:
            if row.court_no is None:
                counts["skipped"] += 1
                continue

            defaults = {
                "court_name": row.bench_desc,
                "address": row.roaster_desc,
                "est_code_src": (row.est_code_src or "")[:6],
            }

            obj, created = Court.objects.update_or_create(id=row.court_no, defaults=defaults)
            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts

    def _migrate_act(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        qs = self._legacy_qs(legacy_models.ActT, limit=limit)
        for row in qs:
            if row.actcode is None:
                counts["skipped"] += 1
                continue

            defaults = {
                "actname": row.actname,
                "lactname": row.lactname,
                "acttype": row.acttype,
                "display": row.display,
                "national_code": (str(row.national_code)[:15] if row.national_code is not None else None),
                "shortact": row.shortact,
                "amd": row.amd,
                "create_modify": row.create_modify,
                "est_code_src": (row.est_code_src or "")[:6],
            }

            obj, created = ActT.objects.update_or_create(actcode=row.actcode, defaults=defaults)
            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts

    def _migrate_case_type(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        qs = self._legacy_qs(legacy_models.CaseTypeT, limit=limit)
        for row in qs:
            if row.case_type is None:
                counts["skipped"] += 1
                continue

            defaults = {
                "case_type": row.case_type,
                "type_name": row.type_name,
                "ltype_name": row.ltype_name,
                "full_form": row.full_form,
                "lfull_form": row.lfull_form,
                "type_flag": row.type_flag,
                "est_code_src": (row.est_code_src or "")[:6],
            }

            # case_type_t in core currently has implicit id PK, so we store case_type as data field.
            existing = CaseTypeT.objects.filter(case_type=row.case_type).first()
            if existing:
                for field, value in defaults.items():
                    setattr(existing, field, value)
                existing.save(update_fields=list(defaults.keys()))
                counts["updated"] += 1
            else:
                CaseTypeT.objects.create(**defaults)
                counts["created"] += 1

        return counts

    def _migrate_civil(self, limit=None):
        counts = {"created": 0, "updated": 0, "skipped": 0}

        qs = self._legacy_qs(legacy_models.CivilT, limit=limit)

        for row in qs:
            if not row.cino:
                counts["skipped"] += 1
                continue

            case_type_obj = None
            if row.filcase_type is not None:
                case_type_obj = CaseTypeT.objects.filter(case_type=row.filcase_type).first()

            defaults = {
                "case_type": case_type_obj,
                "bench": str(row.court_no) if row.court_no is not None else None,
                "petitioner_name": row.pet_name,
                "petitioner_contact": (row.pet_mobile or "")[:10] if row.pet_mobile else None,
                "e_filing_number": row.efilno,
                "is_draft": False,
            }

            # Upsert by stable legacy identifier currently mapped into e_filing_number when available.
            # Fallback to create when no efilno exists.
            if row.efilno:
                obj, created = core_models.Efiling.objects.update_or_create(e_filing_number=row.efilno, defaults=defaults)
            else:
                core_models.Efiling.objects.create(**defaults)
                created = True

            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts
