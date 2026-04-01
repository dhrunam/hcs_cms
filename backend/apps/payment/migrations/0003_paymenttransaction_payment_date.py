from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0002_paymenttransaction_offline_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymenttransaction",
            name="payment_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]

