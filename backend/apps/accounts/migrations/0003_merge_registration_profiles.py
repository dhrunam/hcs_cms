# Merge PartyInPersonProfile + AdvocateRegistrationProfile into RegistrationProfile

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def copy_profiles_forward(apps, schema_editor):
    Party = apps.get_model("accounts", "PartyInPersonProfile")
    Advocate = apps.get_model("accounts", "AdvocateRegistrationProfile")
    RegistrationProfile = apps.get_model("accounts", "RegistrationProfile")

    for p in Party.objects.all():
        RegistrationProfile.objects.create(
            user_id=p.user_id,
            date_of_birth=p.date_of_birth,
            address=p.address,
            gender=p.gender,
            photo=p.photo,
            bar_id="",
            bar_id_file=None,
            verification_status="",
        )

    for a in Advocate.objects.all():
        if RegistrationProfile.objects.filter(user_id=a.user_id).exists():
            continue
        RegistrationProfile.objects.create(
            user_id=a.user_id,
            date_of_birth=a.date_of_birth,
            address=a.address,
            gender=a.gender,
            photo=a.photo,
            bar_id=a.bar_id,
            bar_id_file=a.bar_id_file,
            verification_status=a.verification_status,
        )


def copy_profiles_backward(apps, schema_editor):
    """Best-effort restore into split tables (verification '' -> party)."""
    RegistrationProfile = apps.get_model("accounts", "RegistrationProfile")
    Party = apps.get_model("accounts", "PartyInPersonProfile")
    Advocate = apps.get_model("accounts", "AdvocateRegistrationProfile")

    for r in RegistrationProfile.objects.all():
        if (r.bar_id or "").strip() or r.bar_id_file or (
            r.verification_status and r.verification_status != ""
        ):
            Advocate.objects.create(
                user_id=r.user_id,
                date_of_birth=r.date_of_birth,
                address=r.address,
                gender=r.gender,
                photo=r.photo,
                bar_id=r.bar_id or "",
                bar_id_file=r.bar_id_file,
                verification_status=r.verification_status or "pending",
            )
        else:
            Party.objects.create(
                user_id=r.user_id,
                date_of_birth=r.date_of_birth,
                address=r.address,
                gender=r.gender,
                photo=r.photo,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_jwt_auth_profiles"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistrationProfile",
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
                        blank=True, null=True, upload_to="profiles/registration/"
                    ),
                ),
                ("bar_id", models.CharField(blank=True, default="", max_length=128)),
                (
                    "bar_id_file",
                    models.FileField(
                        blank=True, null=True, upload_to="advocate/bar_id/"
                    ),
                ),
                (
                    "verification_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "Not applicable"),
                            ("pending", "Pending"),
                            ("verified", "Verified"),
                            ("rejected", "Rejected"),
                        ],
                        default="",
                        max_length=16,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registration_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registration profile",
                "verbose_name_plural": "Registration profiles",
            },
        ),
        migrations.RunPython(copy_profiles_forward, copy_profiles_backward),
        migrations.DeleteModel(name="AdvocateRegistrationProfile"),
        migrations.DeleteModel(name="PartyInPersonProfile"),
    ]
