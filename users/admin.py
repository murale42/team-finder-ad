from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "avatar_preview",
        "email",
        "name",
        "surname",
        "is_staff",
        "is_active",
    )

    list_filter = ("is_staff", "is_active")

    ordering = ("email",)

    search_fields = ("email", "name", "surname")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "surname", "avatar", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    @admin.display(description="Avatar")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.avatar.url,
            )
        return "-"
