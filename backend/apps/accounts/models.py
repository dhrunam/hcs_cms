from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.roles import REGISTRATION_TYPE_CHOICES


class User(AbstractUser):
    """
    Custom user model for the HCS Case Management System.
    Uses email as the primary login identifier.
    """

    email = models.EmailField(unique=True, verbose_name="Email address")
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone number",
    )
    department = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Department",
    )
    designation = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Designation",
    )
    registration_type = models.CharField(
        max_length=32,
        blank=True,
        choices=REGISTRATION_TYPE_CHOICES,
        default="",
        verbose_name="Registration type",
    )
    email_verified = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["email"]

    def __str__(self) -> str:
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.email


class RegistrationProfile(models.Model):
    """
    Single profile table for self-registered party-in-person and advocate users.
    Advocate-only fields (bar_id, bar_id_file, verification_status) are empty for parties.
    """

    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
        ("U", "Prefer not to say"),
    )

    VERIFICATION_PENDING = "pending"
    VERIFICATION_VERIFIED = "verified"
    VERIFICATION_REJECTED = "rejected"
    VERIFICATION_CHOICES = (
        ("", "Not applicable"),
        (VERIFICATION_PENDING, "Pending"),
        (VERIFICATION_VERIFIED, "Verified"),
        (VERIFICATION_REJECTED, "Rejected"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registration_profile",
    )
    date_of_birth = models.DateField()
    address = models.TextField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    photo = models.FileField(
        upload_to="profiles/registration/", blank=True, null=True
    )
    bar_id = models.CharField(max_length=128, blank=True, default="")
    bar_id_file = models.FileField(
        upload_to="advocate/bar_id/", blank=True, null=True
    )
    verification_status = models.CharField(
        max_length=16,
        choices=VERIFICATION_CHOICES,
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = "Registration profile"
        verbose_name_plural = "Registration profiles"

    def __str__(self) -> str:
        return f"Registration profile: {self.user.email}"
