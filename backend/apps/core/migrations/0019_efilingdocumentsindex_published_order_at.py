from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_orderdetailsa_created_at_orderdetailsa_created_by_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="efilingdocumentsindex",
            name="published_order_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When a court/steno order became final (signed publish); use for display in case files.",
                null=True,
            ),
        ),
    ]
