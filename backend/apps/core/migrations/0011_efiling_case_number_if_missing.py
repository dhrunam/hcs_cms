"""
Recover DBs where e_filing exists but case_number column is missing (migration drift).
Safe: no-op if case_number already exists.
"""

from django.db import migrations, models


def add_case_number_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    table = "e_filing"
    with connection.cursor() as cursor:
        cols = connection.introspection.get_table_description(cursor, table)
        names = {c.name for c in cols}
    if "case_number" in names:
        return
    Efiling = apps.get_model("core", "Efiling")
    field = models.CharField(max_length=120, unique=True, blank=True, null=True)
    field.set_attributes_from_name("case_number")
    schema_editor.add_field(Efiling, field)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_create_reader_judge_assignment_if_missing"),
    ]

    operations = [
        migrations.RunPython(add_case_number_if_missing, noop_reverse),
    ]
