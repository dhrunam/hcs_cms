from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_efiling_has_payment_objection_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='efiling',
            name='has_payment_objection',
        ),
        migrations.RemoveField(
            model_name='efiling',
            name='objection_resolved_by_payment',
        ),
        migrations.RemoveField(
            model_name='efiling',
            name='payment_objection_amount',
        ),
    ]