from . import models

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "timedelta",
        "active",
        "owner",
        "url",
    )
    list_filter = ("owner", "active")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter),)

    def refresh(self, request, queryset):
        for obj in queryset:
            obj.refresh()

    refresh.short_description = "Refresh cached counters"
    actions = ["refresh"]


@admin.register(models.Pomodoro)
class PomodoroAdmin(admin.ModelAdmin):
    date_hierarchy = "start"
    list_select_related = ("project", "owner")
    list_display = (
        "title",
        "project",
        "start",
        "end",
        "duration",
        "owner",
    )
    list_filter = (
        "start",
        ("owner", admin.RelatedOnlyFieldListFilter),
        ("project", admin.RelatedOnlyFieldListFilter),
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_select_related = ("project", "owner")
    list_display = (
        "title",
        "project",
        "timedelta",
        "owner",
        "count",
        "url",
    )
    list_filter = (
        ("owner", admin.RelatedOnlyFieldListFilter),
        ("project", admin.RelatedOnlyFieldListFilter),
    )

    def refresh(self, request, queryset):
        for obj in queryset:
            obj.refresh()

    refresh.short_description = "Refresh cached counters"
    actions = ["refresh"]


@admin.register(models.Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("pk", "owner", "last_accessed")
    readonly_fields = ("last_accessed",)
