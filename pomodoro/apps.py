import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PomodoroConfig(AppConfig):
    name = "pomodoro"

    def ready(self):
        try:
            import pomodoro.signals  # noqa
        except ImportError as e:
            logger.exception("Unable to import pomodoro %s", e)
