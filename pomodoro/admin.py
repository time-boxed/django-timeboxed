from . import models

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "active", "owner")
    list_filter = ("owner", "active")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter),)


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
    list_display = ("title", "project", "duration", "owner", "count")
    list_filter = (
        ("owner", admin.RelatedOnlyFieldListFilter),
        ("project", admin.RelatedOnlyFieldListFilter),
    )


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("owner", "type")


@admin.register(models.Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("pk", "owner", "last_accessed")
    readonly_fields = ("last_accessed",)
