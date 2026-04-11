"""Drop drf_sso_resource SSOUserProfile table and migration rows before removing the app."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_efilingdocuments_filed_by"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS drf_sso_resource_ssouserprofile;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DELETE FROM django_migrations WHERE app = 'drf_sso_resource';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
