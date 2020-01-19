import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PomodoroConfig(AppConfig):
    name = 'pomodoro'

    def ready(self):
        import pomodoro.tasks  # NOQA
        import pomodoro.signals  # NOQA
