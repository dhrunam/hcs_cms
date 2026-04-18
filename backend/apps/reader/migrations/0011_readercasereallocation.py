from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apps.reader.models


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0010_readerdailyproceeding_steno_purpose"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReaderCaseReallocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("previous_bench_key", models.CharField(max_length=50)),
                ("new_bench_key", models.CharField(max_length=50)),
                ("remarks", models.TextField()),
                ("uploaded_order", models.FileField(blank=True, max_length=512, null=True, upload_to=apps.reader.models._reader_case_reallocation_order_upload_to)),
                ("reallocated_at", models.DateTimeField()),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_created", to=settings.AUTH_USER_MODEL)),
                ("efiling", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reader_case_reallocations", to="core.efiling")),
                ("reallocated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reader_case_reallocations", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_updated", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "reader_case_reallocation",
                "indexes": [models.Index(fields=["efiling", "reallocated_at"], name="reader_case__efiling_dfa191_idx"), models.Index(fields=["previous_bench_key", "new_bench_key"], name="reader_case__previou_63f2ec_idx")],
            },
        ),
    ]