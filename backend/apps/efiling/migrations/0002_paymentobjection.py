from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('efiling', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentObjection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('court_fee_amount', models.DecimalField(decimal_places=2, help_text='The correct court fee amount as determined by the scrutiny officer', max_digits=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('RESOLVED', 'Resolved'), ('CANCELLED', 'Cancelled')], db_index=True, default='PENDING', max_length=20)),
                ('remarks', models.TextField(blank=True, help_text='Optional remarks explaining the payment objection', null=True)),
                ('raised_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, help_text='Timestamp when the objection was resolved', null=True)),
                ('e_filing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_objections', to='core.efiling')),
                ('raised_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raised_payment_objections', to='accounts.user')),
            ],
            options={
                'verbose_name': 'Payment Objection',
                'verbose_name_plural': 'Payment Objections',
                'db_table': 'efiling_payment_objection',
                'ordering': ['-raised_at'],
            },
        ),
    ]
