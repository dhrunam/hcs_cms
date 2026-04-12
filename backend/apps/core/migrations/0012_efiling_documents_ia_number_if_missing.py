"""
Recover DBs where efiling_documents exists but ia_number column is missing (migration drift).
Safe: no-op if ia_number already exists.
"""

from django.db import migrations, models


def add_ia_number_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    table = "efiling_documents"
    with connection.cursor() as cursor:
        cols = connection.introspection.get_table_description(cursor, table)
        names = {c.name for c in cols}
    if "ia_number" in names:
        return
    EfilingDocuments = apps.get_model("core", "EfilingDocuments")
    field = models.CharField(max_length=100, blank=True, null=True)
    field.set_attributes_from_name("ia_number")
    schema_editor.add_field(EfilingDocuments, field)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_efiling_case_number_if_missing"),
    ]

    operations = [
        migrations.RunPython(add_ia_number_if_missing, noop_reverse),
    ]
