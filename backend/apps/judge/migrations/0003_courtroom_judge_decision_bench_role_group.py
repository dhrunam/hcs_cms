# Generated manually for courtroom approval flow

from django.db import migrations, models


def backfill_bench_role_groups(apps, schema_editor):
    from apps.core.bench_config import get_required_judge_groups

    Decision = apps.get_model("judge", "CourtroomJudgeDecision")
    Forward = apps.get_model("reader", "CourtroomForward")
    User = apps.get_model("accounts", "User")

    token_names = frozenset({"JUDGE_CJ", "JUDGE_J1", "JUDGE_J2"})

    for dec in Decision.objects.filter(bench_role_group__isnull=True).iterator():
        fwd = (
            Forward.objects.filter(
                efiling_id=dec.efiling_id,
                forwarded_for_date=dec.forwarded_for_date,
            )
            .order_by("-id")
            .first()
        )
        if not fwd:
            continue
        required = tuple(get_required_judge_groups(fwd.bench_key))
        if not required:
            continue
        try:
            user = User.objects.get(pk=dec.judge_user_id)
        except User.DoesNotExist:
            continue
        names = set(user.groups.values_list("name", flat=True))
        matched = names & set(required) & token_names
        role = None
        if len(matched) == 1:
            role = next(iter(matched))
        elif len(matched) > 1:
            role = sorted(matched)[0]
        elif "API_JUDGE" in names and len(required) == 1:
            role = required[0]
        if role:
            Decision.objects.filter(pk=dec.pk).update(bench_role_group=role)


class Migration(migrations.Migration):

    dependencies = [
        ("judge", "0002_courtroomsharedview"),
        ("reader", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="courtroomjudgedecision",
            name="bench_role_group",
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
        migrations.RunPython(backfill_bench_role_groups, migrations.RunPython.noop),
    ]
