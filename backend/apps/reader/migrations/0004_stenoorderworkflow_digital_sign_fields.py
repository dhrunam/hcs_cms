from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0003_rename_reader_daily_bench_k_0f7c26_idx_reader_dail_bench_k_0e416e_idx_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digital_signature_certificate_serial",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digital_signature_metadata",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digital_signature_provider",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digital_signature_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digital_signature_signer_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digitally_signed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="digitally_signed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="steno_digitally_signed_workflows",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

