from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('efiling', '0002_paymentobjection'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentobjection',
            name='resolved_by_payment_id',
            field=models.CharField(
                blank=True,
                help_text='The payment transaction ID that resolved this objection',
                max_length=100,
                null=True
            ),
        ),
    ]
