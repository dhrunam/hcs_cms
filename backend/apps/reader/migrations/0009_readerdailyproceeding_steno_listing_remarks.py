from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0008_backfill_courtroom_forward_bench_role_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="readerdailyproceeding",
            name="listing_remark",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="readerdailyproceeding",
            name="steno_remark",
            field=models.TextField(blank=True, null=True),
        ),
    ]
