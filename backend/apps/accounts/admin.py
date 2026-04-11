from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import RegistrationProfile, User


@admin.register(RegistrationProfile)
class RegistrationProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth", "gender", "bar_id", "verification_status")
    list_filter = ("verification_status", "gender")
    search_fields = ("user__email", "bar_id")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "phone_number",
                    "department",
                    "designation",
                    "registration_type",
                    "email_verified",
                ),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": ("email", "phone_number", "department", "designation"),
            },
        ),
    )

    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "department",
        "designation",
        "is_staff",
        "is_active",
    ]
    list_filter = ["is_staff", "is_active", "department"]
    search_fields = ["email", "username", "first_name", "last_name", "department"]
    ordering = ["email"]
