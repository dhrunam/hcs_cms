from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_purposet"),
        ("reader", "0009_readerdailyproceeding_steno_listing_remarks"),
    ]

    operations = [
        migrations.AddField(
            model_name="readerdailyproceeding",
            name="steno_purpose",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="reader_daily_proceedings",
                to="core.purposet",
            ),
        ),
    ]