from django.conf import settings
from django.db import models


class SSOUserProfile(models.Model):
    """
    Stores the SSO subject identifier (``sub`` claim) and the raw token
    claims for a Django user.

    This model is optional.  If your project already has an equivalent
    model, set ``SSO_USER_PROFILE_MODEL = "myapp.MyProfile"`` in settings
    and remove this app's migrations from your migration graph (or keep them
    — the table is simply never written to).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sso_profile",
    )
    sso_id = models.CharField(max_length=255, unique=True, db_index=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "drf_sso_resource"
        verbose_name = "SSO User Profile"
        verbose_name_plural = "SSO User Profiles"

    def __str__(self) -> str:
        return f"SSOProfile({self.user_id}, sub={self.sso_id!r})"
