from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": ("phone_number", "department", "designation"),
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
