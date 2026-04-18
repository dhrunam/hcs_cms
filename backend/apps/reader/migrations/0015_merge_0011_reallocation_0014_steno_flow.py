# Merge parallel reader branches (ReaderCaseReallocation vs steno/signature chain).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reader", "0011_readercasereallocation"),
        ("reader", "0014_stenoorderworkflow_senior_judge_flow"),
    ]

    operations = []
