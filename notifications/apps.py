import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PomodoroConfig(AppConfig):
    name = "notifications"

    def ready(self):
        from . import tasks  # NOQA
