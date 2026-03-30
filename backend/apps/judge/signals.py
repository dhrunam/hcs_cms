from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_judge_seed_data(sender, app_config=None, **kwargs):
    """
    Seed judge groups/users after migrations.

    This runs only when DB schema is available and avoids querying DB in AppConfig.ready().
    """
    if app_config and app_config.name != "apps.judge":
        return

    for group_name in ["JUDGE_CJ", "JUDGE_J1", "JUDGE_J2"]:
        Group.objects.get_or_create(name=group_name)

    user_model = get_user_model()
    email_field = user_model._meta.get_field("email")
    if not getattr(email_field, "unique", False):
        # Project-auth model should have unique email for safe get_or_create.
        return

    dummy_users = [
        {
            "email": "dummy_judge_cj@hcs.local",
            "username": "dummy_judge_cj",
            "first_name": "Dummy",
            "last_name": "CJ",
            "group": "JUDGE_CJ",
        },
        {
            "email": "dummy_judge_j1@hcs.local",
            "username": "dummy_judge_j1",
            "first_name": "Dummy",
            "last_name": "Judge-I",
            "group": "JUDGE_J1",
        },
        {
            "email": "dummy_judge_j2@hcs.local",
            "username": "dummy_judge_j2",
            "first_name": "Dummy",
            "last_name": "Judge-II",
            "group": "JUDGE_J2",
        },
    ]

    for data in dummy_users:
        user, _ = user_model.objects.get_or_create(
            email=data["email"],
            defaults={
                "username": data["username"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "is_active": True,
            },
        )
        group = Group.objects.get(name=data["group"])
        if not user.groups.filter(name=group.name).exists():
            user.groups.add(group)

