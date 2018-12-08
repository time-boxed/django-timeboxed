from pomodoro.models import Favorite, Notification, Pomodoro, Tag

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter),)


@admin.register(Pomodoro)
class PomodoroAdmin(admin.ModelAdmin):
    date_hierarchy = "start"
    list_display = ("title", "_tags", "start", "end", "duration", "owner")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter), "start")

    def _tags(self, obj):
        return [t.title for t in obj.tags.all()]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    def _icon(self, obj):
        return True if obj.icon else False

    _icon.short_description = _("icon")
    _icon.boolean = True

    def _tags(self, obj):
        return [t.title for t in obj.tags.all()]

    list_display = ("title", "_tags", "duration", "owner", "_icon", "count")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter),)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("owner", "type")
