from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0012_stenoworkflowsignature_forward_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="signed_upload",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="signed_upload_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="signed_upload_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="steno_signed_upload_signature_rows",
                to="accounts.user",
            ),
        ),
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="signed_upload_note",
            field=models.TextField(blank=True, null=True),
        ),
    ]
