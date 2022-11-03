from . import models

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("owner", "type")
