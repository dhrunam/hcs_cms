from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.models import CaseTypeT, DocumentIndex


class Command(BaseCommand):
    help = (
        'Import new-filing DocumentIndex rows from '
        'backend/config/new_filing_document_index.json. '
        'Each JSON object label is the case_type number and each array item '
        'must provide Sl. No. and Item values.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default=str(
                Path(settings.BASE_DIR)
                / 'config'
                / 'new_filing_document_index.json'
            ),
            help='Path to the document index JSON file.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and validate the file without writing database changes.',
        )

    def handle(self, *args, **options):
        json_path = Path(options['path']).resolve()
        dry_run = options['dry_run']

        if not json_path.exists():
            raise CommandError(f'JSON file not found: {json_path}')

        payload = self._load_payload(json_path)
        created_count = 0
        updated_count = 0
        skipped_missing_case_type = 0
        duplicate_entries_ignored = 0

        with transaction.atomic():
            for label_case_type, items in payload.items():
                case_type_code = self._parse_case_type_label(
                    label_case_type,
                )
                case_type = CaseTypeT.objects.filter(
                    case_type=case_type_code,
                ).order_by('id').first()

                if case_type is None:
                    skipped_missing_case_type += 1
                    self.stdout.write(
                        self.style.WARNING(
                            'Skipping label '
                            f'{case_type_code}: no matching CaseTypeT.case_type found.'
                        ),
                    )
                    continue

                seen_keys: set[tuple[int, str]] = set()
                for raw_item in items:
                    sequence_number = self._parse_sequence_number(
                        raw_item['Sl. No.'],
                        case_type_code=case_type_code,
                    )
                    normalized_name = self._normalize_name(raw_item['Item'])
                    if not normalized_name:
                        continue

                    dedupe_key = (sequence_number, normalized_name)
                    if dedupe_key in seen_keys:
                        duplicate_entries_ignored += 1
                        continue
                    seen_keys.add(dedupe_key)

                    document_index, created = self._upsert_document_index(
                        case_type=case_type,
                        sequence_number=sequence_number,
                        name=normalized_name,
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += self._update_document_index(
                            document_index=document_index,
                            name=normalized_name,
                            sequence_number=sequence_number,
                        )

            if dry_run:
                transaction.set_rollback(True)

        suffix = 'Dry run complete.' if dry_run else 'Import complete.'
        self.stdout.write(self.style.SUCCESS(suffix))
        self.stdout.write(f'Created rows: {created_count}')
        self.stdout.write(f'Updated rows: {updated_count}')
        self.stdout.write(
            f'Missing CaseTypeT rows skipped: {skipped_missing_case_type}'
        )
        self.stdout.write(
            f'Duplicate JSON entries ignored: {duplicate_entries_ignored}'
        )

    def _load_payload(self, json_path: Path) -> dict[str, list[dict[str, str]]]:
        try:
            with json_path.open('r', encoding='utf-8') as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON in {json_path}: {exc}') from exc

        if not isinstance(payload, dict):
            raise CommandError('Top-level JSON value must be an object.')

        for label_case_type, items in payload.items():
            if not isinstance(items, list):
                raise CommandError(
                    'Each JSON label must map to an array of objects. '
                    f'Problem label: {label_case_type}'
                )
            for raw_item in items:
                if not isinstance(raw_item, dict):
                    raise CommandError(
                        'Each array item must be an object with Sl. No. and Item. '
                        f'Problem label: {label_case_type}'
                    )
                if 'Sl. No.' not in raw_item or 'Item' not in raw_item:
                    raise CommandError(
                        'Each array object must contain Sl. No. and Item keys. '
                        f'Problem label: {label_case_type}'
                    )
                if not isinstance(raw_item['Item'], str):
                    raise CommandError(
                        'Item must be a string value. '
                        f'Problem label: {label_case_type}'
                    )

        return payload

    def _parse_case_type_label(self, raw_case_type: str) -> int:
        try:
            return int(str(raw_case_type).strip())
        except ValueError as exc:
            raise CommandError(
                f'Invalid case_type label in JSON: {raw_case_type!r}'
            ) from exc

    def _parse_sequence_number(
        self,
        raw_sequence_number,
        *,
        case_type_code: int,
    ) -> int:
        try:
            return int(str(raw_sequence_number).strip())
        except ValueError as exc:
            raise CommandError(
                'Invalid Sl. No. value '
                f'{raw_sequence_number!r} for case_type {case_type_code}.'
            ) from exc

    def _normalize_name(self, raw_name: str) -> str:
        return ' '.join(str(raw_name).split()).strip()

    def _upsert_document_index(
        self,
        *,
        case_type: CaseTypeT,
        sequence_number: int,
        name: str,
    ) -> tuple[DocumentIndex, bool]:
        existing = DocumentIndex.objects.filter(
            case_type=case_type,
            sequence_number=sequence_number,
        ).order_by('id').first()
        if existing:
            return existing, False

        existing = DocumentIndex.objects.filter(
            case_type=case_type,
            name=name,
        ).order_by('id').first()
        if existing:
            return existing, False

        return DocumentIndex.objects.create(
            case_type=case_type,
            sequence_number=sequence_number,
            name=name,
            for_new_filing=True,
        ), True

    def _update_document_index(
        self,
        *,
        document_index: DocumentIndex,
        name: str,
        sequence_number: int,
    ) -> int:
        update_fields: list[str] = []

        if document_index.name != name:
            document_index.name = name
            update_fields.append('name')

        if document_index.sequence_number != sequence_number:
            document_index.sequence_number = sequence_number
            update_fields.append('sequence_number')

        if not document_index.for_new_filing:
            document_index.for_new_filing = True
            update_fields.append('for_new_filing')

        if not update_fields:
            return 0

        document_index.save(update_fields=[*update_fields, 'updated_at'])
        return 1