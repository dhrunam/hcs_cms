"""
Recover from DBs where core.0001 is applied but reader_judge_assignment was never created
(or was dropped). Requires judge_t (0008). Safe: no-op if the table already exists.
"""

from django.db import migrations


def create_reader_judge_assignment_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
    if "reader_judge_assignment" in tables:
        return
    ReaderJudgeAssignment = apps.get_model("core", "ReaderJudgeAssignment")
    schema_editor.create_model(ReaderJudgeAssignment)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_create_bench_t_if_missing"),
    ]

    operations = [
        migrations.RunPython(create_reader_judge_assignment_if_missing, noop_reverse),
    ]
