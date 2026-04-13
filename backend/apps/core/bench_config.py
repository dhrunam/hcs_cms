from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Optional

from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User

from .models import BenchT, ReaderJudgeAssignment

# Opaque per-slot identifiers for a bench bucket (order matches judge_names / judge_user_ids).
MAX_BENCH_JUDGES = 3
GENERIC_JUDGE_GROUP = 'JUDGE'


def bench_slot_group(slot_index: int) -> str:
    if slot_index < 0 or slot_index >= MAX_BENCH_JUDGES:
        raise ValueError(f'bench slot index must be 0..{MAX_BENCH_JUDGES - 1}')
    return f'BENCH_S{slot_index}'


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


_READER_ROLE_GROUP_NAMES = frozenset({'READER'})


def resolved_efiling_bench_value(config: BenchConfiguration) -> str:
    """Canonical value for Efiling.bench: prefer bench_code when present."""
    if config.bench_code and str(config.bench_code).strip():
        return str(config.bench_code).strip()
    return config.bench_key


def _is_authenticated_reader_user(user: User | None) -> bool:
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    names = set(user.groups.values_list('name', flat=True))
    return bool(names & _READER_ROLE_GROUP_NAMES)


def _active_reader_assignments_qs(user_id: int, as_of_date=None):
    active_date = as_of_date or timezone.localdate()
    return ReaderJudgeAssignment.objects.filter(
        reader_user_id=user_id,
        effective_from__lte=active_date,
    ).filter(
        Q(effective_to__isnull=True) | Q(effective_to__gte=active_date),
    )


def _hydrate_reader_fields_from_assignments(
    config: BenchConfiguration,
    as_of_date=None,
) -> BenchConfiguration:
    """Set reader_user_ids / reader_user_ids_by_group from reader_judge_assignment only."""
    if not config.judge_user_ids:
        return replace(
            config,
            reader_user_ids=tuple(),
            reader_user_ids_by_group=tuple(),
        )

    active_date = as_of_date or timezone.localdate()
    qs = (
        ReaderJudgeAssignment.objects.filter(
            judge__user_id__in=config.judge_user_ids,
            effective_from__lte=active_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=active_date))
        .select_related('judge')
    )

    by_judge_user_id: dict[int, int] = {}
    for row in qs:
        ju = getattr(row.judge, 'user_id', None)
        if ju:
            by_judge_user_id[int(ju)] = int(row.reader_user_id)

    reader_user_ids: list[int] = []
    by_group: dict[str, int] = {}
    for i, ju in enumerate(config.judge_user_ids):
        rid = by_judge_user_id.get(int(ju))
        if rid is None:
            continue
        if rid not in reader_user_ids:
            reader_user_ids.append(rid)
        if i < len(config.judge_groups):
            by_group[config.judge_groups[i]] = rid

    return replace(
        config,
        reader_user_ids=tuple(reader_user_ids),
        reader_user_ids_by_group=tuple(by_group.items()),
    )


def _bench_keys_for_reader_assignments(
    user: User,
    configs: list[BenchConfiguration],
    as_of_date=None,
) -> set[str]:
    """Bench keys for configs that include a judge tied to an active ReaderJudgeAssignment."""
    keys: set[str] = set()
    qs = _active_reader_assignments_qs(user.id, as_of_date).select_related(
        'judge__user',
    )
    for row in qs:
        ju = getattr(row.judge, 'user_id', None)
        if not ju:
            continue
        for config in configs:
            if ju in config.judge_user_ids:
                keys.add(config.bench_key)
    return keys


def _expand_bench_strings_for_configs(
    configs: list[BenchConfiguration],
    bench_keys: set[str],
) -> set[str]:
    """Include bench_code for each config whose bench_key is allowed (for Efiling.bench matching)."""
    out = set(bench_keys)
    for c in configs:
        if c.bench_key in bench_keys and c.bench_code and str(c.bench_code).strip():
            out.add(str(c.bench_code).strip())
    return out


def _reader_scope_bench_keys_merged(
    user: User,
    configs: list[BenchConfiguration],
    as_of_date=None,
) -> set[str]:
    return _bench_keys_for_reader_assignments(
        user,
        configs,
        as_of_date=as_of_date,
    )


def mapped_judge_names_for_reader(
    bench: BenchConfiguration,
    user: User | None,
    as_of_date=None,
) -> tuple[str, ...]:
    """
    Judges this reader is assigned to via reader_judge_assignment (active window),
    aligned with bench.judge_names / judge_user_ids by slot.
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return bench.judge_names

    qs = _active_reader_assignments_qs(user.id, as_of_date).select_related(
        'judge',
    )
    assigned_judge_user_ids = {
        int(row.judge.user_id)
        for row in qs
        if getattr(row, 'judge', None) and row.judge.user_id
    }
    if not assigned_judge_user_ids:
        return bench.judge_names

    names_by_assignment: list[str] = []
    for name, ju in zip(bench.judge_names, bench.judge_user_ids):
        if int(ju) in assigned_judge_user_ids:
            names_by_assignment.append(name)
    if names_by_assignment:
        return tuple(names_by_assignment)

    return bench.judge_names


def _active_bench_rows(as_of_date=None):
    active_date = as_of_date or timezone.localdate()
    return (
        BenchT.objects.filter(is_active=True, from_date__lte=active_date)
        .filter(Q(to_date__isnull=True) | Q(to_date__gte=active_date))
        .select_related('judge__user')
        .prefetch_related('judge__user__groups')
        .filter(Q(judge__isnull=False))
        .order_by('bench_code', 'id')
        .distinct()
    )


def _judge_user_eligible_for_bench(user: User | None) -> bool:
    if not user:
        return False
    group_names = {group.name for group in user.groups.all()}
    return GENERIC_JUDGE_GROUP in group_names


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
    """
    One configuration per bench_t bucket (bench_code). Judge order follows seniority
    within the bucket. Slots use opaque names BENCH_S0, BENCH_S1, …
    """
    by_code: dict[str, list] = defaultdict(list)
    for bench_row in _active_bench_rows(as_of_date=as_of_date):
        code = (bench_row.bench_code or '').strip() or None
        bucket_key = code if code else f'row-{bench_row.id}'
        by_code[bucket_key].append(bench_row)

    result: list[BenchConfiguration] = []
    for bucket_key in sorted(by_code.keys(), key=str):
        bench_rows = by_code[bucket_key]
        eligible: list = []
        for br in bench_rows:
            ju = getattr(br.judge, 'user', None)
            if _judge_user_eligible_for_bench(ju):
                eligible.append(br)
        eligible.sort(
            key=lambda br: (
                br.judge.seniority is None,
                br.judge.seniority if br.judge.seniority is not None else 0,
                br.judge_id,
            ),
        )
        eligible = eligible[:MAX_BENCH_JUDGES]
        if not eligible:
            continue

        first = bench_rows[0]
        bench_code = (first.bench_code or '').strip() or None
        bench_name = (first.bench_name or '').strip() or None
        bench_key = bench_code if bench_code else str(bucket_key)

        judge_names: list[str] = []
        judge_user_ids: list[int] = []
        judge_groups: list[str] = []
        for slot_index, bench_row in enumerate(eligible):
            judge_groups.append(bench_slot_group(slot_index))
            judge_names.append(_judge_display_name(bench_row))
            ju = getattr(getattr(bench_row.judge, 'user', None), 'id', None)
            if ju:
                judge_user_ids.append(int(ju))

        label = bench_name or bench_key
        result.append(
            BenchConfiguration(
                bench_key=bench_key,
                label=label,
                bench_code=bench_code,
                bench_name=bench_name,
                judge_names=tuple(judge_names),
                judge_user_ids=tuple(judge_user_ids),
                judge_groups=tuple(judge_groups),
                reader_user_ids=tuple(),
                reader_user_ids_by_group=tuple(),
            ),
        )

    return sorted(result, key=lambda x: x.bench_key)


def get_bench_configurations(as_of_date=None) -> list[BenchConfiguration]:
    configs = _build_active_bench_configurations(as_of_date=as_of_date)
    return [
        _hydrate_reader_fields_from_assignments(c, as_of_date=as_of_date)
        for c in configs
    ]


def get_bench_configuration(
    bench_key: str,
    as_of_date=None,
) -> BenchConfiguration | None:
    for item in get_bench_configurations(as_of_date=as_of_date):
        if item.bench_key == bench_key:
            return item
    return get_bench_configuration_for_stored_value(bench_key, as_of_date=as_of_date)


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


def judge_user_seated_on_bench_key(
    user: User | None,
    forward_bench_key: str | None,
    as_of_date=None,
) -> bool:
    """
    True if this user is one of the seated judges on the active bench bucket for forward_bench_key.
    Uses JudgeT-linked user ids on BenchConfiguration (not Django role groups).
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    bk = str(forward_bench_key or '').strip()
    if not bk:
        return False
    config = get_bench_configuration(bk, as_of_date=as_of_date)
    if not config:
        config = get_bench_configuration_for_stored_value(bk, as_of_date=as_of_date)
    if not config or not config.judge_user_ids:
        return False
    uid = int(user.pk)
    return uid in {int(x) for x in config.judge_user_ids}


def bench_key_aliases_for_seated_judge(
    user: User | None,
    as_of_date=None,
) -> set[str]:
    """
    Strings that may appear as CourtroomForward.bench_key / CauseList.bench_key for benches
    this user is seated on (canonical key, bench_code, resolved efiling value).
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return set()
    uid = int(user.pk)
    out: set[str] = set()
    for c in get_bench_configurations(as_of_date=as_of_date):
        if uid not in {int(x) for x in c.judge_user_ids}:
            continue
        out.add(c.bench_key)
        if c.bench_code and str(c.bench_code).strip():
            out.add(str(c.bench_code).strip())
        out.add(resolved_efiling_bench_value(c))
    return out


def resolve_bench_for_registration(
    bench_value: str | None,
    as_of_date=None,
) -> BenchConfiguration:
    """
    Resolve scrutiny bench input to an active configuration.
    Persist resolved_efiling_bench_value(cfg) on Efiling.bench.
    """
    normalized = str(bench_value or '').strip()
    if not normalized:
        raise ValueError('Bench is required to register the case.')
    cfg = get_bench_configuration_for_stored_value(normalized, as_of_date=as_of_date)
    if not cfg:
        raise ValueError(
            f'Unknown or inactive bench {normalized!r}. Choose a bench from the active list.',
        )
    return cfg


_BENCH_SLOT_RE = re.compile(r'^BENCH_S\d+$')


def get_required_judge_groups(
    bench_key: str,
    as_of_date=None,
) -> tuple[str, ...]:
    bk = str(bench_key or '').strip()
    if _BENCH_SLOT_RE.match(bk):
        return (bk,)
    bench = get_bench_configuration(bk, as_of_date=as_of_date)
    if not bench:
        return tuple()
    return bench.judge_groups


def _reader_bench_slots_for_user(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> set[str]:
    del reader_group
    slots: set[str] = set()
    if not user or not getattr(user, 'is_authenticated', False):
        return slots

    for config in get_bench_configurations(as_of_date=as_of_date):
        for slot_group, reader_user_id in config.reader_user_ids_by_group:
            if reader_user_id == user.id:
                slots.add(slot_group)

    return slots


def get_primary_bench_slot_group(bench_key: str, as_of_date=None) -> str | None:
    bench = get_bench_configuration(bench_key, as_of_date=as_of_date)
    if bench and bench.judge_groups:
        return bench.judge_groups[0]
    return None


def is_reader_date_authority_for_bench(
    bench_key: str,
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> bool:
    bench = get_bench_configuration(bench_key, as_of_date=as_of_date)
    if not bench or not bench.judge_groups:
        return False

    primary_slot = bench.judge_groups[0]
    if user and getattr(user, 'is_authenticated', False):
        for slot_g, reader_user_id in bench.reader_user_ids_by_group:
            if slot_g == primary_slot:
                return reader_user_id == user.id

    return primary_slot in _reader_bench_slots_for_user(
        user,
        reader_group=reader_group,
        as_of_date=as_of_date,
    )


def get_accessible_bench_keys_for_reader(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> Optional[set[str]]:
    del reader_group
    configs = get_bench_configurations(as_of_date=as_of_date)

    if user and getattr(user, 'is_authenticated', False):
        merged = _reader_scope_bench_keys_merged(user, configs, as_of_date=as_of_date)
        if merged:
            return _expand_bench_strings_for_configs(configs, merged)

        if _active_reader_assignments_qs(user.id, as_of_date).exists():
            return set()

        if _is_authenticated_reader_user(user):
            return set()

        return None

    return None


def get_accessible_bench_codes_for_reader(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> Optional[set[str]]:
    """Subset of get_accessible_bench_keys_for_reader: entries that are bench_code values."""
    keys = get_accessible_bench_keys_for_reader(
        user,
        reader_group=reader_group,
        as_of_date=as_of_date,
    )
    if keys is None:
        return None
    codes = set()
    for c in get_bench_configurations(as_of_date=as_of_date):
        if c.bench_code and str(c.bench_code).strip() in keys:
            codes.add(str(c.bench_code).strip())
    return codes


def get_forward_bench_keys_for_reader(
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> set[str]:
    del reader_group
    configs = get_bench_configurations(as_of_date=as_of_date)

    if user and getattr(user, 'is_authenticated', False):
        scope_keys_raw = _reader_scope_bench_keys_merged(
            user,
            configs,
            as_of_date=as_of_date,
        )
        if not scope_keys_raw:
            return set()
        direct_keys = {
            config.bench_key
            for config in configs
            if len(config.judge_groups) == 1 and config.bench_key in scope_keys_raw
        }
        if direct_keys:
            return direct_keys
        assignment_keys = {
            config.bench_key
            for config in configs
            if len(config.judge_groups) > 1 and config.bench_key in scope_keys_raw
        }
        if assignment_keys:
            return assignment_keys

    return set()


def is_reader_allowed_for_bench(
    bench_key: str,
    user: User | None,
    reader_group: str | None = None,
    as_of_date=None,
) -> bool:
    allowed = get_accessible_bench_keys_for_reader(
        user,
        reader_group=reader_group,
        as_of_date=as_of_date,
    )
    if allowed is None:
        return True
    if bench_key in allowed:
        return True
    cfg = get_bench_configuration_for_stored_value(bench_key, as_of_date=as_of_date)
    if cfg:
        return resolved_efiling_bench_value(cfg) in allowed
    return False
