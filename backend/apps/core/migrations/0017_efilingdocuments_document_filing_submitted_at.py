from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_casetypet_annexure_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="efilingdocuments",
            name="document_filing_submitted_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Set when advocate completes document filing (fee + submit-filing) for existing-case uploads.",
                null=True,
            ),
        ),
    ]
