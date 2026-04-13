"""
Recover from DBs where django_migrations shows core.0001 applied but judge_t was never created
(or was dropped). Safe to run: no-op if judge_t already exists.
"""

from django.db import migrations


def create_judge_t_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
    if "judge_t" in tables:
        return
    JudgeT = apps.get_model("core", "JudgeT")
    schema_editor.create_model(JudgeT)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_remove_drf_sso_resource_table"),
    ]

    operations = [
        migrations.RunPython(create_judge_t_if_missing, noop_reverse),
    ]
