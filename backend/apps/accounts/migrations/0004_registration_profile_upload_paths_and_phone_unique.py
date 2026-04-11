# Generated for RegistrationProfile upload_to + User phone uniqueness.

from django.db import migrations, models
from django.db.models import Q

import apps.accounts.models as accounts_models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_merge_registration_profiles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registrationprofile",
            name="photo",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=accounts_models.registration_profile_photo_upload_to,
            ),
        ),
        migrations.AlterField(
            model_name="registrationprofile",
            name="bar_id_file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=accounts_models.registration_profile_bar_id_upload_to,
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                fields=("phone_number",),
                condition=Q(phone_number__gt=""),
                name="accounts_user_phone_unique_when_set",
            ),
        ),
    ]
