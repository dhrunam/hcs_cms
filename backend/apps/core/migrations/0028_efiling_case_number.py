from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0027_repair_advocatet_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="efiling",
            name="case_number",
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
    ]
