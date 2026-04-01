from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymenttransaction",
            name="payment_mode",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="paymenttransaction",
            name="court_fees",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="paymenttransaction",
            name="bank_receipt",
            field=models.FileField(blank=True, null=True, upload_to="payment/"),
        ),
    ]

