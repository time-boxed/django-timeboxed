import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PomodoroConfig(AppConfig):
    name = 'pomodoro'

    def ready(self):
        try:
            import pomodoro.tasks
        except ImportError as e:
            logger.warning('Unable to import pomodoro %s', e)
