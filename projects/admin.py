from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "participants_count", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "owner__email")

    @admin.display(description="Участники")
    def participants_count(self, obj):
        return obj.participants.count()
