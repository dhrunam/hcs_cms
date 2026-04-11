from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User

from .models import BenchT


JUDGE_GROUP_TO_BENCH_TOKEN = {
    'JUDGE_CJ': 'CJ',
    'JUDGE_J1': 'Judge1',
    'JUDGE_J2': 'Judge2',
}

BENCH_TOKEN_TO_JUDGE_GROUP = {
    value: key for key, value in JUDGE_GROUP_TO_BENCH_TOKEN.items()
}
BENCH_TOKEN_ORDER = ['CJ', 'Judge1', 'Judge2']

LEGACY_BENCH_LABELS = {
    'CJ': "Hon'ble Chief Justice",
    'Judge1': "Hon'ble Judge - I",
    'Judge2': "Hon'ble Judge - II",
    'CJ+Judge1': 'Division Bench I',
    'CJ+Judge2': 'Division Bench II',
    'Judge1+Judge2': 'Division Bench III',
    'CJ+Judge1+Judge2': 'Full Bench',
}

LEGACY_READER_GROUP_TO_TOKENS = {
    'READER_CJ': {'CJ'},
    'READER_J1': {'Judge1'},
    'READER_J2': {'Judge2'},
}

LEGACY_JUDGE_DISPLAY_NAMES = {
    'CJ': "Hon'ble Chief Justice",
    'Judge1': "Hon'ble Judge - I",
    'Judge2': "Hon'ble Judge - II",
}


@dataclass(frozen=True)
class BenchConfiguration:
    bench_key: str
    label: str
    bench_code: str | None
    bench_name: str | None
    judge_names: tuple[str, ...]
    judge_user_ids: tuple[int, ...]
    judge_groups: tuple[str, ...]
    reader_user_ids: tuple[int, ...]
    reader_user_ids_by_group: tuple[tuple[str, int], ...] = tuple()


def _ordered_tokens(tokens: Iterable[str]) -> list[str]:
    unique_tokens = {token for token in tokens if token in BENCH_TOKEN_ORDER}
    return [token for token in BENCH_TOKEN_ORDER if token in unique_tokens]


def _active_bench_rows(as_of_date=None):
    active_date = as_of_date or timezone.localdate()
    return (
        BenchT.objects.filter(is_active=True, from_date__lte=active_date)
        .filter(Q(to_date__isnull=True) | Q(to_date__gte=active_date))
        .select_related('judge__user', 'judge__reader_assignment__reader_user')
        .prefetch_related(
            'judge__user__groups',
            'judge__reader_assignment__reader_user__groups',
        )
        .filter(Q(judge__isnull=False))
        .order_by('bench_code', 'id')
        .distinct()
    )


def _judge_group_name(user: User | None) -> str | None:
    if not user:
        return None
    group_names = {group.name for group in user.groups.all()}
    for group_name in JUDGE_GROUP_TO_BENCH_TOKEN:
        if group_name in group_names:
            return group_name
    return None


def _judge_display_name(bench_row: BenchT) -> str:
    judge = bench_row.judge
    if not judge:
        return ''
    if judge.judge_name:
        return judge.judge_name
    user = getattr(judge, 'user', None)
    if user:
        full_name = user.get_full_name().strip()
        if full_name:
            return full_name
        if user.email:
            return user.email
    return judge.judge_code


def _build_active_bench_configurations(
    as_of_date=None,
) -> list[BenchConfiguration]:
    by_key: dict[str, dict] = {}

    for bench_row in _active_bench_rows(as_of_date=as_of_date):
        group_name = _judge_group_name(getattr(bench_row.judge, 'user', None))
        if not group_name:
            continue
        token = JUDGE_GROUP_TO_BENCH_TOKEN[group_name]
        bench_code = (bench_row.bench_code or '').strip() or None
        bench_name = (bench_row.bench_name or '').strip() or None
        group_bucket = by_key.setdefault(
            bench_code or f'row-{bench_row.id}',
            {
                'bench_code': bench_code,
                'bench_name': bench_name,
                'tokens': [],
                'judge_names': [],
                'judge_user_ids': [],
                'judge_groups': [],
                'reader_user_ids': [],
                'reader_user_ids_by_group': {},
            },
        )
        if token not in group_bucket['tokens']:
            group_bucket['tokens'].append(token)
        judge_name = _judge_display_name(bench_row)
        if judge_name and judge_name not in group_bucket['judge_names']:
            group_bucket['judge_names'].append(judge_name)
        judge_user_id = getattr(
            getattr(bench_row.judge, 'user', None),
            'id',
            None,
        )
        if (
            judge_user_id
            and judge_user_id not in group_bucket['judge_user_ids']
        ):
            group_bucket['judge_user_ids'].append(judge_user_id)
        if group_name not in group_bucket['judge_groups']:
            group_bucket['judge_groups'].append(group_name)
        assignment = getattr(bench_row.judge, 'reader_assignment', None)
        if (
            assignment
            and assignment.reader_user_id
            and assignment.reader_user_id
            not in group_bucket['reader_user_ids']
        ):
            group_bucket['reader_user_ids'].append(assignment.reader_user_id)
        if assignment and assignment.reader_user_id:
            group_bucket['reader_user_ids_by_group'][
                group_name
            ] = assignment.reader_user_id

    merged: dict[str, BenchConfiguration] = {}
    for bucket in by_key.values():
        ordered_tokens = _ordered_tokens(bucket['tokens'])
        if not ordered_tokens:
            continue
        bench_key = '+'.join(ordered_tokens)
        existing = merged.get(bench_key)
        judge_names = tuple(bucket['judge_names'])
        judge_user_ids = tuple(bucket['judge_user_ids'])
        judge_groups = tuple(
            BENCH_TOKEN_TO_JUDGE_GROUP[token]
            for token in ordered_tokens
        )
        reader_user_ids = tuple(bucket['reader_user_ids'])
        reader_user_ids_by_group = tuple(
            (group_name, int(reader_user_id))
            for group_name, reader_user_id in (
                bucket['reader_user_ids_by_group'].items()
            )
        )
        label = bucket['bench_name'] or LEGACY_BENCH_LABELS.get(
            bench_key,
            bench_key,
        )

        if existing:
            merged_reader_user_ids_by_group = dict(
                existing.reader_user_ids_by_group
            )
            merged_reader_user_ids_by_group.update(
                dict(reader_user_ids_by_group)
            )
            merged[bench_key] = BenchConfiguration(
                bench_key=bench_key,
                label=existing.label,
                bench_code=existing.bench_code,
                bench_name=existing.bench_name,
                judge_names=tuple(
                    dict.fromkeys([*existing.judge_names, *judge_names])
                ),
                judge_user_ids=tuple(
                    dict.fromkeys([
                        *existing.judge_user_ids,
                        *judge_user_ids,
                    ])
                ),
                judge_groups=existing.judge_groups,
                reader_user_ids=tuple(
                    dict.fromkeys([
                        *existing.reader_user_ids,
                        *reader_user_ids,
                    ])
                ),
                reader_user_ids_by_group=tuple(
                    merged_reader_user_ids_by_group.items()
                ),
            )
            continue

        merged[bench_key] = BenchConfiguration(
            bench_key=bench_key,
            label=label,
            bench_code=bucket['bench_code'],
            bench_name=bucket['bench_name'],
            judge_names=judge_names,
            judge_user_ids=judge_user_ids,
            judge_groups=judge_groups,
            reader_user_ids=reader_user_ids,
            reader_user_ids_by_group=reader_user_ids_by_group,
        )

    return sorted(
        merged.values(),
        key=lambda item: (
            len(item.judge_groups),
            [
                BENCH_TOKEN_ORDER.index(token)
                for token in item.bench_key.split('+')
            ],
        ),
    )


def _legacy_required_groups(bench_key: str) -> tuple[str, ...]:
    tokens = _ordered_tokens(bench_key.split('+'))
    return tuple(BENCH_TOKEN_TO_JUDGE_GROUP[token] for token in tokens)


def _legacy_bench_configurations() -> list[BenchConfiguration]:
    items: list[BenchConfiguration] = []
    for bench_key, label in LEGACY_BENCH_LABELS.items():
        tokens = bench_key.split('+')
        items.append(
            BenchConfiguration(
                bench_key=bench_key,
                label=label,
                bench_code=None,
                bench_name=None,
                judge_names=tuple(
                    LEGACY_JUDGE_DISPLAY_NAMES.get(token, token)
                    for token in tokens
                ),
                judge_user_ids=tuple(),
                judge_groups=_legacy_required_groups(bench_key),
                reader_user_ids=tuple(),
                reader_user_ids_by_group=tuple(),
            ),
        )
    return items


def get_bench_configurations(as_of_date=None) -> list[BenchConfiguration]:
    configs = _build_active_bench_configurations(as_of_date=as_of_date)
    return configs or _legacy_bench_configurations()


def get_bench_configuration(
    bench_key: str,
    as_of_date=None,
) -> BenchConfiguration | None:
    for item in get_bench_configurations(as_of_date=as_of_date):
        if item.bench_key == bench_key:
            return item
    legacy_groups = _legacy_required_groups(bench_key)
    if not legacy_groups:
        return None
    return BenchConfiguration(
        bench_key=bench_key,
        label=LEGACY_BENCH_LABELS.get(bench_key, bench_key),
        bench_code=None,
        bench_name=None,
        judge_names=tuple(
            LEGACY_BENCH_LABELS.get(token, token)
            for token in bench_key.split('+')
        ),
        judge_user_ids=tuple(),
        judge_groups=legacy_groups,
        reader_user_ids=tuple(),
        reader_user_ids_by_group=tuple(),
    )


def get_bench_configuration_for_stored_value(
    bench_value: str | None,
    as_of_date=None,
) -> BenchConfiguration | None:
    normalized_value = str(bench_value or '').strip()
    if not normalized_value:
        return None

    for item in get_bench_configurations(as_of_date=as_of_date):
        if item.bench_key == normalized_value:
            return item
        if item.bench_code and item.bench_code == normalized_value:
            return item

    return None


def get_required_judge_groups(
    bench_key: str,
    as_of_date=None,
) -> tuple[str, ...]:
    bench = get_bench_configuration(bench_key, as_of_date=as_of_date)
    if not bench:
        return tuple()
    return bench.judge_groups


def resolve_reader_slot_group_for_user(
    user: User | None,
    bench_key: str,
    *,
    reader_group: str | None = None,
    as_of_date=None,
) -> str:
    """
    Resolve CourtroomForward.reader_slot_group (canonical judge group, e.g. JUDGE_CJ).

    Uses per-bench reader→slot mapping when present, else legacy READER_* query param,
    else the sole slot on single-judge benches. Division benches require an explicit
    mapping or reader_slot_group in the API payload.
    """
    bench_config = get_bench_configuration(bench_key, as_of_date=as_of_date)
    if not bench_config:
        raise ValueError(f'Unknown bench_key={bench_key!r}.')

    if user and getattr(user, 'is_authenticated', False):
        mapping = dict(bench_config.reader_user_ids_by_group or ())
        for group_name, reader_user_id in mapping.items():
            if int(reader_user_id) == int(user.id):
                return str(group_name)

    if reader_group:
        for token in LEGACY_READER_GROUP_TO_TOKENS.get(reader_group, set()):
            group_name = BENCH_TOKEN_TO_JUDGE_GROUP.get(token)
            if group_name and group_name in set(bench_config.judge_groups):
                return str(group_name)

    required = tuple(bench_config.judge_groups or ())
    if len(required) == 1:
        return str(required[0])

    raise ValueError(
        'Cannot infer reader slot for this division bench; send reader_slot_group in the '
        'request body or map this reader user to a judge slot in bench configuration.'
    )


def _legacy_reader_tokens(
    user: User | None,
    reader_group: str | None = None,
) -> set[str]:
    tokens: set[str] = set()
    if user and getattr(user, 'is_authenticated', False):
        for group_name in user.groups.values_list('name', flat=True):
            tokens.update(LEGACY_READER_GROUP_TO_TOKENS.get(group_name, set()))
    if reader_group:
        tokens.update(LEGACY_READER_GROUP_TO_TOKENS.get(reader_group, set()))
    return tokens


def _reader_tokens_for_user(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> set[str]:
    tokens = _legacy_reader_tokens(user, reader_group=reader_group)
    if not user or not getattr(user, 'is_authenticated', False):
        return tokens

    for config in get_bench_configurations(as_of_date=as_of_date):
        for judge_group, reader_user_id in config.reader_user_ids_by_group:
            if reader_user_id == user.id:
                token = JUDGE_GROUP_TO_BENCH_TOKEN.get(judge_group)
                if token:
                    tokens.add(token)

    return tokens


def get_primary_bench_token(bench_key: str, as_of_date=None) -> str | None:
    bench = get_bench_configuration(bench_key, as_of_date=as_of_date)
    if bench and bench.judge_groups:
        tokens = [
            JUDGE_GROUP_TO_BENCH_TOKEN[group_name]
            for group_name in bench.judge_groups
            if group_name in JUDGE_GROUP_TO_BENCH_TOKEN
        ]
        if tokens:
            return tokens[0]

    tokens = _ordered_tokens(str(bench_key or '').split('+'))
    return tokens[0] if tokens else None


def is_reader_date_authority_for_bench(
    bench_key: str,
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> bool:
    primary_token = get_primary_bench_token(bench_key, as_of_date=as_of_date)
    if not primary_token:
        return False

    primary_group = BENCH_TOKEN_TO_JUDGE_GROUP.get(primary_token)
    bench = get_bench_configuration(bench_key, as_of_date=as_of_date)
    if (
        user
        and getattr(user, 'is_authenticated', False)
        and bench
        and primary_group
    ):
        for judge_group, reader_user_id in bench.reader_user_ids_by_group:
            if judge_group == primary_group:
                return reader_user_id == user.id

    return primary_token in _reader_tokens_for_user(
        user,
        reader_group=reader_group,
        as_of_date=as_of_date,
    )


def get_accessible_bench_keys_for_reader(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> Optional[set[str]]:
    configs = get_bench_configurations(as_of_date=as_of_date)
    if user and getattr(user, 'is_authenticated', False):
        user_bench_keys = {
            config.bench_key
            for config in configs
            if user.id in config.reader_user_ids
        }
        if user_bench_keys:
            return user_bench_keys

    legacy_tokens = _legacy_reader_tokens(user, reader_group=reader_group)
    if legacy_tokens:
        return {
            config.bench_key
            for config in configs
            if legacy_tokens & set(config.bench_key.split('+'))
        } or {
            bench_key
            for bench_key in LEGACY_BENCH_LABELS
            if legacy_tokens & set(bench_key.split('+'))
        }

    return None


def get_accessible_bench_codes_for_reader(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> Optional[set[str]]:
    configs = get_bench_configurations(as_of_date=as_of_date)
    accessible_keys = get_accessible_bench_keys_for_reader(
        user,
        reader_group=reader_group,
        as_of_date=as_of_date,
    )
    if accessible_keys is None:
        return None

    codes = {
        config.bench_code
        for config in configs
        if config.bench_key in accessible_keys and config.bench_code
    }
    return codes or None


def get_forward_bench_keys_for_reader(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> set[str]:
    configs = get_bench_configurations(as_of_date=as_of_date)

    if user and getattr(user, 'is_authenticated', False):
        direct_keys = {
            config.bench_key
            for config in configs
            if (
                len(config.judge_groups) == 1
                and user.id in config.reader_user_ids
            )
        }
        if direct_keys:
            return direct_keys

    legacy_tokens = _legacy_reader_tokens(user, reader_group=reader_group)
    if not legacy_tokens:
        return set()

    config_keys = {
        config.bench_key
        for config in configs
        if len(config.judge_groups) == 1 and config.bench_key in legacy_tokens
    }
    return config_keys or legacy_tokens


def is_reader_allowed_for_bench(
    bench_key: str,
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> bool:
    allowed_bench_keys = get_accessible_bench_keys_for_reader(
        user,
        reader_group=reader_group,
        as_of_date=as_of_date,
    )
    if allowed_bench_keys is None:
        return True
    return bench_key in allowed_bench_keys
