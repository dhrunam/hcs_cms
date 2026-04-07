# Adds annotation_data when DB predates the column (schema drift vs 0001_initial).

from django.db import connection, migrations


def add_annotation_data_if_missing(apps, schema_editor):
    table = "courtroom_document_annotation"
    column = "annotation_data"
    quoted_table = connection.ops.quote_name(table)
    quoted_column = connection.ops.quote_name(column)

    with connection.cursor() as cursor:
        if connection.vendor == "postgresql":
            cursor.execute(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = %s
                  AND column_name = %s
                """,
                [table, column],
            )
            if cursor.fetchone():
                return
            cursor.execute(
                f"ALTER TABLE {quoted_table} ADD COLUMN {quoted_column} jsonb NULL"
            )
            return

        if connection.vendor == "sqlite":
            cursor.execute(f"PRAGMA table_info({table})")
            cols = {row[1] for row in cursor.fetchall()}
            if column in cols:
                return
            cursor.execute(
                f"ALTER TABLE {quoted_table} ADD COLUMN {quoted_column} TEXT NULL"
            )
            return

        # Add a matching migration for other backends if needed.
        return


class Migration(migrations.Migration):

    dependencies = [
        ("judge", "0003_courtroom_judge_decision_bench_role_group"),
    ]

    operations = [
        migrations.RunPython(add_annotation_data_if_missing, migrations.RunPython.noop),
    ]
