from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_efiling_documents_index_scrutiny_columns_if_missing"),
    ]

    operations = [
        migrations.CreateModel(
            name="CaseAccessRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("case_number", models.CharField(max_length=120)),
                (
                    "vakalatnama_document",
                    models.FileField(max_length=512, upload_to="media/efile/case-access-requests/"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")],
                        db_index=True,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("rejection_reason", models.TextField(blank=True, null=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "advocate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="case_access_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "approved_access",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="source_requests",
                        to="core.efilerdocumentaccess",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "e_filing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="case_access_requests",
                        to="core.efiling",
                    ),
                ),
                (
                    "resubmission_of",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reapplications",
                        to="core.caseaccessrequest",
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_case_access_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "case_access_request",
                "ordering": ["-id"],
            },
        ),
    ]
