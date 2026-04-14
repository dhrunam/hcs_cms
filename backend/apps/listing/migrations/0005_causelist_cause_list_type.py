from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listing", "0004_cause_list_date_status_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="causelist",
            name="cause_list_type",
            field=models.CharField(
                choices=[("DAILY", "Daily"), ("SUPPLEMENTARY", "Supplementary")],
                default="DAILY",
                max_length=20,
            ),
        ),
    ]
