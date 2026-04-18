"""Ensure efiling_documents.document_filing_submitted_at exists (fixes drift if 0017 was marked applied without DDL)."""

from django.db import migrations


def ensure_column(apps, schema_editor):
    connection = schema_editor.connection
    table = "efiling_documents"
    col = "document_filing_submitted_at"

    with connection.cursor() as cursor:
        if connection.vendor == "postgresql":
            cursor.execute(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = %s
                  AND column_name = %s
                """,
                [table, col],
            )
            if cursor.fetchone():
                return
            cursor.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{col}" TIMESTAMP WITH TIME ZONE NULL'
            )
        elif connection.vendor == "sqlite":
            cursor.execute(f'PRAGMA table_info("{table}")')
            names = [row[1] for row in cursor.fetchall()]
            if col in names:
                return
            cursor.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{col}" datetime NULL'
            )
        else:
            cursor.execute(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table, col],
            )
            if cursor.fetchone():
                return
            cursor.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{col}" TIMESTAMP NULL'
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_merge_0017_efilingdocuments_0019_published_order"),
    ]

    operations = [
        migrations.RunPython(ensure_column, noop_reverse),
    ]
