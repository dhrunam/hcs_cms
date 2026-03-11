from django.contrib.auth.models import AbstractUser
from django.db import models


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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["email"]

    def __str__(self) -> str:
        full_name = self.get_full_name().strip()
        return full_name if full_name else self.email
