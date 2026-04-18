# Generated manually for division senior-judge steno gate

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0013_stenoworkflowsignature_signed_upload_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="draft_last_submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="draft_last_submitted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="steno_draft_submitted_workflows",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="senior_judge_decided_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="senior_judge_decided_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="steno_senior_judge_decided_workflows",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="senior_judge_remarks",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stenoorderworkflow",
            name="senior_judge_returned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stenoorderworkflow",
            name="workflow_status",
            field=models.CharField(
                choices=[
                    ("PENDING_UPLOAD", "Pending Upload"),
                    ("UPLOADED_BY_STENO", "Uploaded by Steno"),
                    ("SENT_FOR_JUDGE_APPROVAL", "Sent for Judge Approval"),
                    ("PENDING_SENIOR_JUDGE_APPROVAL", "Pending Senior Judge Approval"),
                    ("RETURNED_BY_SENIOR_JUDGE", "Returned by Senior Judge"),
                    ("CHANGES_REQUESTED", "Changes Requested"),
                    ("JUDGE_APPROVED", "Judge Approved"),
                    ("SHARED_FOR_SIGNATURE", "Shared For Signature"),
                    ("SIGNATURES_IN_PROGRESS", "Signatures In Progress"),
                    ("SIGNED_AND_PUBLISHED", "Signed and Published"),
                ],
                default="PENDING_UPLOAD",
                max_length=40,
            ),
        ),
    ]
