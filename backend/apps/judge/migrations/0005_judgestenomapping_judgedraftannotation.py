import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judge", "0004_courtroom_document_annotation_annotation_data"),
        ("reader", "0002_readerdailyproceeding_stenoorderworkflow"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JudgeStenoMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("bench_key", models.CharField(blank=True, max_length=50, null=True)),
                ("effective_from", models.DateField()),
                ("effective_to", models.DateField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_created", to=settings.AUTH_USER_MODEL)),
                ("judge_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="judge_steno_mappings", to=settings.AUTH_USER_MODEL)),
                ("steno_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="steno_judge_mappings", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_updated", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "judge_steno_mapping"},
        ),
        migrations.CreateModel(
            name="JudgeDraftAnnotation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("page_number", models.IntegerField(blank=True, null=True)),
                ("x", models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ("y", models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ("width", models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ("height", models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ("annotation_type", models.CharField(choices=[("COMMENT", "Comment"), ("HIGHLIGHT", "Highlight"), ("TEXT_REPLACE", "Text Replace"), ("FORMAT", "Format")], default="COMMENT", max_length=20)),
                ("note_text", models.TextField()),
                ("status", models.CharField(choices=[("OPEN", "Open"), ("RESOLVED", "Resolved")], default="OPEN", max_length=20)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="judge_draft_annotations_created", to=settings.AUTH_USER_MODEL)),
                ("resolved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="judge_draft_annotations_resolved", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_updated", to=settings.AUTH_USER_MODEL)),
                ("workflow", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="judge_annotations", to="reader.stenoorderworkflow")),
            ],
            options={"db_table": "judge_draft_annotation"},
        ),
        migrations.AddIndex(
            model_name="judgestenomapping",
            index=models.Index(fields=["judge_user", "is_active"], name="judge_steno_judge_u_b28982_idx"),
        ),
        migrations.AddIndex(
            model_name="judgestenomapping",
            index=models.Index(fields=["steno_user", "is_active"], name="judge_steno_steno_u_8e1451_idx"),
        ),
        migrations.AddIndex(
            model_name="judgestenomapping",
            index=models.Index(fields=["bench_key"], name="judge_steno_bench_k_4569d0_idx"),
        ),
        migrations.AddIndex(
            model_name="judgestenomapping",
            index=models.Index(fields=["effective_from", "effective_to"], name="judge_steno_effecti_5194b9_idx"),
        ),
        migrations.AddIndex(
            model_name="judgedraftannotation",
            index=models.Index(fields=["workflow", "status"], name="judge_draft_workflo_346b69_idx"),
        ),
        migrations.AddIndex(
            model_name="judgedraftannotation",
            index=models.Index(fields=["created_by"], name="judge_draft_created_4284be_idx"),
        ),
    ]
