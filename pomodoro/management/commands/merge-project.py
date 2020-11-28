from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from pomodoro import models


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("src")
        parser.add_argument("dst")
        parser.add_argument("--force", action="store_true")

    def project(self, username, name):
        try:
            return models.Project.objects.get(
                owner__username=username, name__iexact=name
            )
        except ObjectDoesNotExist:
            raise CommandError("No Project %s" % name)

    def handle(self, username, src, dst, force, **options):
        src = self.project(username, src)
        dst = self.project(username, dst)
        if force:
            src.pomodoro_set.update(project=dst)
            src.favorite_set.update(project=dst)
        else:
            self.stdout.write("Pomodoros %d" % src.pomodoro_set.count())
            self.stdout.write("Favorites %d" % src.favorite_set.count())
