"""
Recover DBs where efiling_documents_index is missing draft/scrutiny columns (migration drift).
Adds any of: scrutiny_status, draft_scrutiny_status, draft_comments, draft_reviewed_at,
is_new_for_scrutiny, last_resubmitted_at, last_reviewed_at, parent_document_index.
Safe: skips columns that already exist.
"""

import django.db.models.deletion
from django.db import migrations, models

SCRUTINY_CHOICES = [
    ("DRAFT", "Draft"),
    ("UNDER_SCRUTINY", "Under Scrutiny"),
    ("LEVEL_1_APPROVED", "Level 1 Approved"),
    ("LEVEL_1_REJECTED", "Level 1 Rejected"),
    ("LEVEL_2_APPROVED", "Level 2 Approved"),
    ("LEVEL_2_REJECTED", "Level 2 Rejected"),
    ("ACCEPTED", "Accepted"),
    ("REJECTED", "Rejected"),
]


def add_missing_scrutiny_columns(apps, schema_editor):
    connection = schema_editor.connection
    table = "efiling_documents_index"
    with connection.cursor() as cursor:
        cols = connection.introspection.get_table_description(cursor, table)
        names = {c.name for c in cols}

    EfilingDocumentsIndex = apps.get_model("core", "EfilingDocumentsIndex")

    def add_if_missing(db_column: str, field):
        if db_column in names:
            return
        schema_editor.add_field(EfilingDocumentsIndex, field)
        names.add(db_column)

    # scrutiny_status
    f = models.CharField(
        max_length=32,
        choices=SCRUTINY_CHOICES,
        default="DRAFT",
    )
    f.set_attributes_from_name("scrutiny_status")
    add_if_missing(f.column, f)

    # draft_scrutiny_status
    f = models.CharField(
        max_length=32,
        choices=SCRUTINY_CHOICES,
        blank=True,
        null=True,
    )
    f.set_attributes_from_name("draft_scrutiny_status")
    add_if_missing(f.column, f)

    f = models.TextField(blank=True, null=True)
    f.set_attributes_from_name("draft_comments")
    add_if_missing(f.column, f)

    f = models.DateTimeField(blank=True, null=True)
    f.set_attributes_from_name("draft_reviewed_at")
    add_if_missing(f.column, f)

    f = models.BooleanField(default=False)
    f.set_attributes_from_name("is_new_for_scrutiny")
    add_if_missing(f.column, f)

    f = models.DateTimeField(blank=True, null=True)
    f.set_attributes_from_name("last_resubmitted_at")
    add_if_missing(f.column, f)

    f = models.DateTimeField(blank=True, null=True)
    f.set_attributes_from_name("last_reviewed_at")
    add_if_missing(f.column, f)

    # Self-FK stored as parent_document_index_id
    f = models.ForeignKey(
        EfilingDocumentsIndex,
        on_delete=django.db.models.deletion.SET_NULL,
        null=True,
        blank=True,
        related_name="resubmissions",
    )
    f.set_attributes_from_name("parent_document_index")
    add_if_missing(f.column, f)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_efiling_documents_ia_number_if_missing"),
    ]

    operations = [
        migrations.RunPython(add_missing_scrutiny_columns, noop_reverse),
    ]
