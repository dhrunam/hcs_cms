# Generated manually for per-slot division forwards

from django.db import migrations, models


def backfill_reader_slot_group(apps, schema_editor):
    CourtroomForward = apps.get_model("reader", "CourtroomForward")
    try:
        from apps.core.bench_config import get_bench_configuration, get_required_judge_groups
    except Exception:
        get_required_judge_groups = None
        get_bench_configuration = None

    for f in CourtroomForward.objects.all().iterator():
        if getattr(f, "reader_slot_group", None):
            s = (f.reader_slot_group or "").strip()
            if s:
                continue
        if not get_required_judge_groups:
            f.reader_slot_group = "JUDGE_CJ"
            f.save(update_fields=["reader_slot_group"])
            continue
        req = tuple(get_required_judge_groups(f.bench_key))
        if not req:
            f.reader_slot_group = "JUDGE_CJ"
        elif len(req) == 1:
            f.reader_slot_group = req[0]
        else:
            bench = get_bench_configuration(f.bench_key)
            matched = None
            if bench and f.forwarded_by_id:
                mapping = dict(bench.reader_user_ids_by_group or ())
                for jg, rid in mapping.items():
                    if rid and int(rid) == int(f.forwarded_by_id):
                        matched = jg
                        break
            f.reader_slot_group = matched or req[0]
        f.save(update_fields=["reader_slot_group"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0006_rename_bench_workf_forward_2c84aa_idx_bench_workf_forward_2c4179_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="courtroomforward",
            name="reader_slot_group",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.RunPython(backfill_reader_slot_group, noop_reverse),
        migrations.AlterField(
            model_name="courtroomforward",
            name="reader_slot_group",
            field=models.CharField(max_length=32),
        ),
        migrations.AddIndex(
            model_name="courtroomforward",
            index=models.Index(
                fields=["forwarded_for_date", "bench_key", "reader_slot_group"],
                name="courtroom_f_forward_8a1b2c_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="courtroomforward",
            constraint=models.UniqueConstraint(
                fields=("efiling", "forwarded_for_date", "bench_key", "reader_slot_group"),
                name="courtroom_forward_unique_efiling_date_bench_slot",
            ),
        ),
    ]
