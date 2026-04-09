import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def forwards_judge_steno_judge_t(apps, schema_editor):
    JudgeStenoMapping = apps.get_model("judge", "JudgeStenoMapping")
    JudgeT = apps.get_model("core", "JudgeT")
    missing = []
    for m in JudgeStenoMapping.objects.all().iterator():
        if m.judge_id:
            continue
        jt = JudgeT.objects.filter(user_id=m.judge_user_id).first()
        if jt:
            m.judge_id = jt.pk
            m.save(update_fields=["judge_id"])
        else:
            missing.append((m.id, m.judge_user_id))
    if missing:
        raise ValueError(
            "JudgeStenoMapping rows could not be linked to JudgeT "
            f"(mapping_id, judge_user_id): {missing!r}. "
            "Ensure each judge_user has a JudgeT with matching user_id before migrating."
        )


class Migration(migrations.Migration):

    dependencies = [
        ("judge", "0005_judgestenomapping_judgedraftannotation"),
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="judgestenomapping",
            name="judge_steno_judge_u_b28982_idx",
        ),
        migrations.AddField(
            model_name="judgestenomapping",
            name="judge",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="steno_mappings",
                to="core.judget",
            ),
        ),
        migrations.RunPython(forwards_judge_steno_judge_t, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="judgestenomapping",
            name="judge_user",
        ),
        migrations.AlterField(
            model_name="judgestenomapping",
            name="judge",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="steno_mappings",
                to="core.judget",
            ),
        ),
        migrations.AddIndex(
            model_name="judgestenomapping",
            index=models.Index(fields=["judge", "is_active"], name="judge_steno_judge_i_7a1c2b_idx"),
        ),
    ]
