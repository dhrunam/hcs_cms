from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0011_alter_stenoorderworkflow_workflow_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="forwarded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="forwarded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="steno_forwarded_signature_rows",
                to="accounts.user",
            ),
        ),
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="forwarded_note",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoworkflowsignature",
            name="forwarded_to_judge",
            field=models.BooleanField(default=False),
        ),
    ]
