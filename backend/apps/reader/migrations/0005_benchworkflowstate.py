from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("core", "0003_documentindex_fee_amount_and_more"),
        ("reader", "0004_stenoorderworkflow_digital_sign_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="BenchWorkflowState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("is_active", models.BooleanField(default=True)),
                ("forwarded_for_date", models.DateField()),
                ("bench_key", models.CharField(max_length=50)),
                ("required_role_groups", models.JSONField(blank=True, default=list)),
                ("decision_by_role", models.JSONField(blank=True, default=dict)),
                ("all_required_approved", models.BooleanField(default=False)),
                ("reader_visible", models.BooleanField(default=False)),
                ("listing_date", models.DateField(blank=True, null=True)),
                ("listing_date_assigned_at", models.DateTimeField(blank=True, null=True)),
                ("listing_remark", models.TextField(blank=True, null=True)),
                ("is_published", models.BooleanField(default=False)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reader_benchworkflowstate_created_set", to="accounts.user")),
                ("efiling", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bench_workflow_states", to="core.efiling")),
                ("listing_assigned_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="listing_assigned_bench_workflow_states", to="accounts.user")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reader_benchworkflowstate_updated_set", to="accounts.user")),
                ("assignable_reader_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assignable_bench_workflow_states", to="accounts.user")),
            ],
            options={
                "db_table": "bench_workflow_state",
                "indexes": [
                    models.Index(fields=["forwarded_for_date", "bench_key"], name="bench_workf_forward_2c84aa_idx"),
                    models.Index(fields=["is_published", "forwarded_for_date"], name="bench_workf_is_publ_96e8f1_idx"),
                    models.Index(fields=["all_required_approved", "bench_key"], name="bench_workf_all_req_54d67e_idx"),
                    models.Index(fields=["efiling", "forwarded_for_date"], name="bench_workf_efiling_a78a6d_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="benchworkflowstate",
            constraint=models.UniqueConstraint(fields=("efiling", "forwarded_for_date", "bench_key"), name="bench_workflow_state_unique_case_date_bench"),
        ),
    ]
