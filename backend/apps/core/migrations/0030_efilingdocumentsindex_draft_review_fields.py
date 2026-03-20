from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0029_remove_vakalatnama_is_final_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="efilingdocumentsindex",
            name="draft_comments",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="efilingdocumentsindex",
            name="draft_reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="efilingdocumentsindex",
            name="draft_scrutiny_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("DRAFT", "Draft"),
                    ("UNDER_SCRUTINY", "Under Scrutiny"),
                    ("ACCEPTED", "Accepted"),
                    ("REJECTED", "Rejected"),
                ],
                max_length=32,
                null=True,
            ),
        ),
    ]
