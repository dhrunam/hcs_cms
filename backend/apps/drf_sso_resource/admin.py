from django.contrib import admin

from .models import SSOUserProfile


@admin.register(SSOUserProfile)
class SSOUserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "sso_id", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "sso_id")
    readonly_fields = ("created_at", "updated_at", "extra_data_pretty")
    list_select_related = ("user",)
    ordering = ("-updated_at",)

    fieldsets = (
        (None, {"fields": ("user", "sso_id")}),
        (
            "Raw token claims",
            {
                "classes": ("collapse",),
                "fields": ("extra_data_pretty",),
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Token claims (JSON)")
    def extra_data_pretty(self, obj):
        import json
        from django.utils.html import format_html

        formatted = json.dumps(obj.extra_data, indent=2, default=str)
        return format_html("<pre style='white-space:pre-wrap'>{}</pre>", formatted)
