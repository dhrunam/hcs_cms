# Generated manually for JWT auth / registration profiles

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="registration_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("party_in_person", "Party in person"),
                    ("advocate", "Advocate"),
                ],
                default="",
                max_length=32,
                verbose_name="Registration type",
            ),
        ),
        migrations.CreateModel(
            name="PartyInPersonProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_of_birth", models.DateField()),
                ("address", models.TextField()),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("M", "Male"),
                            ("F", "Female"),
                            ("O", "Other"),
                            ("U", "Prefer not to say"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "photo",
                    models.FileField(
                        blank=True, null=True, upload_to="profiles/party/"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="party_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Party in person profile",
                "verbose_name_plural": "Party in person profiles",
            },
        ),
        migrations.CreateModel(
            name="AdvocateRegistrationProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_of_birth", models.DateField()),
                ("address", models.TextField()),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("M", "Male"),
                            ("F", "Female"),
                            ("O", "Other"),
                            ("U", "Prefer not to say"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "photo",
                    models.FileField(
                        blank=True, null=True, upload_to="profiles/advocate/"
                    ),
                ),
                ("bar_id", models.CharField(max_length=128)),
                ("bar_id_file", models.FileField(upload_to="advocate/bar_id/")),
                (
                    "verification_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("verified", "Verified"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="advocate_registration_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Advocate registration profile",
                "verbose_name_plural": "Advocate registration profiles",
            },
        ),
    ]
