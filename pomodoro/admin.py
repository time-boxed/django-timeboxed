from django.contrib import admin

from pomodoro.models import Pomodoro


class PomodoroAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration', 'owner', 'created')
    list_filter = ('owner', 'category',)

admin.site.register(Pomodoro, PomodoroAdmin)
