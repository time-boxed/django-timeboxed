from zakka.mixins.command import LoggingMixin

from notifications import shortcuts

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import override_settings


class Command(LoggingMixin, BaseCommand):
    def add_arguments(self, parser):
        celery = parser.add_argument_group("Celery")
        celery.add_argument("--eager", action="store_true")

        notify = parser.add_argument_group("Notification")
        notify.add_argument("--driver")
        notify.add_argument("--title", default="Test Title")
        notify.add_argument("username")
        notify.add_argument("message", nargs="?")

    def handle(self, username, eager, **kwargs):
        owner = get_user_model().objects.get(username=username)

        with override_settings(CELERY_TASK_ALWAYS_EAGER=eager):
            shortcuts.queue(
                owner=owner,
                driver=kwargs["driver"],
                title=kwargs["title"],
                body="test body",
            )
