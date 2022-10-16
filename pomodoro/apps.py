import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PomodoroConfig(AppConfig):
    name = "pomodoro"

    def ready(self):
        import pomodoro.signals  # NOQA
        import pomodoro.signals.notification  # NOQA

        if self.apps.is_installed("dmqtt"):
            import pomodoro.signals.mqtt  # NOQA
