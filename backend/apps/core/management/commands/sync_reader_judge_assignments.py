from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import JudgeT, ReaderJudgeAssignment

# (label_for_log, judge_code) — reader users taken from the READER group in stable id order.
READER_SYNC_ROWS = [
    ('JUDGE_CJ', 'SK0'),
    ('JUDGE_J1', 'HSK0002'),
    ('JUDGE_J2', 'HSK0003'),
]


@dataclass
class SyncResult:
    judge_group: str
    judge_user: str | None
    reader_user: str | None
    judge_code: str
    action: str


class Command(BaseCommand):
    help = (
        'Backfill JudgeT.user and ReaderJudgeAssignment rows. '
        'Assigns readers from the READERS group in id order to each judge_code row.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show the inferred mapping without writing database changes.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        results: list[SyncResult] = []

        readers = list(
            User.objects.filter(groups__name='READER')
            .order_by('id')
            .distinct()
        )
        judges = list(
            User.objects.filter(groups__name='JUDGE')
            .order_by('id')
            .distinct()
        )

        with transaction.atomic():
            for idx, (judge_group, judge_code) in enumerate(READER_SYNC_ROWS):
                reader_user = readers[idx] if idx < len(readers) else None
                judge_user = judges[idx] if idx < len(judges) else None

                judge = JudgeT.objects.filter(
                    judge_code=judge_code,
                ).first()

                if not judge:
                    results.append(
                        SyncResult(
                            judge_group=judge_group,
                            judge_user=getattr(judge_user, 'email', None),
                            reader_user=getattr(reader_user, 'email', None),
                            judge_code=judge_code,
                            action='missing-judge-profile',
                        ),
                    )
                    continue

                if not judge_user or not reader_user:
                    results.append(
                        SyncResult(
                            judge_group=judge_group,
                            judge_user=getattr(judge_user, 'email', None),
                            reader_user=getattr(reader_user, 'email', None),
                            judge_code=judge.judge_code,
                            action='missing-user',
                        ),
                    )
                    continue

                action = 'unchanged'
                if judge.user_id != judge_user.id:
                    action = 'updated-judge-user'
                    if not dry_run:
                        judge.user = judge_user
                        judge.save(update_fields=['user', 'updated_at'])

                assignment_defaults = {
                    'reader_user': reader_user,
                    'effective_from': timezone.localdate(),
                    'effective_to': None,
                    'is_active': True,
                }
                existing_assignment = ReaderJudgeAssignment.objects.filter(
                    judge=judge,
                ).first()
                if existing_assignment is None:
                    action = (
                        'created-assignment'
                        if action == 'unchanged'
                        else 'updated-judge-user-created-assignment'
                    )
                    if not dry_run:
                        ReaderJudgeAssignment.objects.create(
                            judge=judge,
                            **assignment_defaults,
                        )
                elif existing_assignment.reader_user_id != reader_user.id:
                    action = 'updated-assignment'
                    if not dry_run:
                        existing_assignment.reader_user = reader_user
                        existing_assignment.effective_to = None
                        existing_assignment.is_active = True
                        existing_assignment.save(
                            update_fields=[
                                'reader_user',
                                'effective_to',
                                'is_active',
                                'updated_at',
                            ],
                        )

                results.append(
                    SyncResult(
                        judge_group=judge_group,
                        judge_user=judge_user.email,
                        reader_user=reader_user.email,
                        judge_code=judge.judge_code,
                        action=action,
                    ),
                )

            if dry_run:
                transaction.set_rollback(True)

        for result in results:
            self.stdout.write(
                f"{result.judge_group}: judge_code={result.judge_code}, "
                f"judge_user={result.judge_user}, "
                f"reader_user={result.reader_user}, action={result.action}"
            )

        created_count = ReaderJudgeAssignment.objects.count()
        suffix = 'would exist after sync' if dry_run else 'now exist'
        self.stdout.write(
            self.style.SUCCESS(f'{created_count} assignments {suffix}.'),
        )
