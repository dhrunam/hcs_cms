import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_efiling_filing_date_efiling_petitioner_vs_respondent"),
        ("reader", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReaderDailyProceeding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("bench_key", models.CharField(max_length=50)),
                ("hearing_date", models.DateField()),
                ("next_listing_date", models.DateField()),
                ("proceedings_text", models.TextField()),
                ("reader_remark", models.TextField(blank=True, null=True)),
                ("listing_sync_status", models.CharField(choices=[("PENDING", "Pending"), ("SYNCED", "Synced"), ("FAILED", "Failed")], default="PENDING", max_length=20)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_created", to=settings.AUTH_USER_MODEL)),
                ("efiling", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reader_daily_proceedings", to="core.efiling")),
                ("submitted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reader_daily_proceedings_submitted", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_updated", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "reader_daily_proceeding"},
        ),
        migrations.CreateModel(
            name="StenoOrderWorkflow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("document_type", models.CharField(choices=[("ORDER", "Order"), ("JUDGMENT", "Judgment")], default="ORDER", max_length=20)),
                ("workflow_status", models.CharField(choices=[("PENDING_UPLOAD", "Pending Upload"), ("UPLOADED_BY_STENO", "Uploaded by Steno"), ("SENT_FOR_JUDGE_APPROVAL", "Sent for Judge Approval"), ("CHANGES_REQUESTED", "Changes Requested"), ("JUDGE_APPROVED", "Judge Approved"), ("SIGNED_AND_PUBLISHED", "Signed and Published")], default="PENDING_UPLOAD", max_length=40)),
                ("judge_approval_status", models.CharField(choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")], default="PENDING", max_length=20)),
                ("judge_approval_notes", models.TextField(blank=True, null=True)),
                ("judge_approved_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("assigned_steno", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_steno_workflows", to=settings.AUTH_USER_MODEL)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_created", to=settings.AUTH_USER_MODEL)),
                ("draft_document_index", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="steno_draft_workflows", to="core.efilingdocumentsindex")),
                ("efiling", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="steno_workflows", to="core.efiling")),
                ("judge_approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="judge_approved_steno_workflows", to=settings.AUTH_USER_MODEL)),
                ("proceeding", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="steno_workflows", to="reader.readerdailyproceeding")),
                ("signed_document_index", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="steno_signed_workflows", to="core.efilingdocumentsindex")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_updated", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "steno_order_workflow"},
        ),
        migrations.AddConstraint(
            model_name="readerdailyproceeding",
            constraint=models.UniqueConstraint(fields=("efiling", "hearing_date", "bench_key"), name="reader_daily_proceeding_unique_case_hearing_bench"),
        ),
        migrations.AddConstraint(
            model_name="stenoorderworkflow",
            constraint=models.UniqueConstraint(fields=("proceeding", "document_type"), name="steno_workflow_unique_proceeding_doc_type"),
        ),
        migrations.AddIndex(
            model_name="readerdailyproceeding",
            index=models.Index(fields=["bench_key", "hearing_date"], name="reader_daily_bench_k_0f7c26_idx"),
        ),
        migrations.AddIndex(
            model_name="readerdailyproceeding",
            index=models.Index(fields=["next_listing_date"], name="reader_daily_next_li_b55f0f_idx"),
        ),
        migrations.AddIndex(
            model_name="stenoorderworkflow",
            index=models.Index(fields=["assigned_steno", "workflow_status"], name="steno_order_assigne_44db2c_idx"),
        ),
        migrations.AddIndex(
            model_name="stenoorderworkflow",
            index=models.Index(fields=["judge_approval_status"], name="steno_order_judge_a_3ff9a6_idx"),
        ),
    ]
