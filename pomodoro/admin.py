from django.contrib import admin
from pomodoro.models import Pomodoro


class PomodoroAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created')

admin.site.register(Pomodoro, PomodoroAdmin)
