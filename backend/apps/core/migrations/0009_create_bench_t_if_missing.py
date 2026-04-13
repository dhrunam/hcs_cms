"""
Recover from DBs where core.0001 is applied but bench_t was never created (or was dropped).
Requires judge_t (see 0008). Safe: no-op if bench_t already exists.
"""

from django.db import migrations


def create_bench_t_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
    if "bench_t" in tables:
        return
    BenchT = apps.get_model("core", "BenchT")
    schema_editor.create_model(BenchT)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_create_judge_t_if_missing"),
    ]

    operations = [
        migrations.RunPython(create_bench_t_if_missing, noop_reverse),
    ]
