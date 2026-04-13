# Generated manually for data backfill

from collections import defaultdict

from django.db import migrations


def backfill_bench_role_group(apps, schema_editor):
    CourtroomForward = apps.get_model("reader", "CourtroomForward")
    try:
        from apps.core.bench_config import get_bench_configuration
    except Exception:  # pragma: no cover
        get_bench_configuration = None

    qs = CourtroomForward.objects.filter(bench_role_group="").order_by("id")
    buckets: dict[tuple, list] = defaultdict(list)
    for fwd in qs:
        buckets[(fwd.efiling_id, fwd.forwarded_for_date, fwd.bench_key)].append(fwd)

    for _key, rows in buckets.items():
        groups: tuple[str, ...] = ()
        if get_bench_configuration and rows:
            cfg = get_bench_configuration(rows[0].bench_key)
            if cfg:
                groups = tuple(cfg.judge_groups or ())

        for i, fwd in enumerate(rows):
            slot = ""
            if get_bench_configuration:
                cfg = get_bench_configuration(fwd.bench_key)
                if cfg:
                    glist = tuple(cfg.judge_groups or ())
                    mapping = dict(cfg.reader_user_ids_by_group or ())
                    uid = getattr(fwd, "forwarded_by_id", None)
                    if uid and mapping:
                        for g, ruid in mapping.items():
                            if int(ruid) == int(uid):
                                slot = str(g)
                                break
                    if not slot and len(glist) == 1:
                        slot = str(glist[0])
                    elif not slot and len(rows) > 1 and i < len(glist):
                        slot = str(glist[i])
                    elif not slot and glist:
                        slot = str(glist[0])
            if not slot:
                slot = "BENCH_S0"
            CourtroomForward.objects.filter(pk=fwd.pk).update(bench_role_group=slot)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0007_courtroom_forward_bench_role_group"),
    ]

    operations = [
        migrations.RunPython(backfill_bench_role_group, noop_reverse),
    ]
