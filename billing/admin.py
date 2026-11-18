from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "is_active",
    )

    list_display_links = ("id", "name")

    search_fields = ("name",)

    list_filter = ("is_active",)

    list_editable = ("price", "is_active")

    fields = (
        "name",
        "description",
        "price",
        "is_active",
    )

    def has_delete_permission(self, request, obj=None):
        return False