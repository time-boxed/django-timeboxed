import collections

from django.core.management.base import BaseCommand

from pomodoro import models


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, username, **options):
        __project_cache = collections.defaultdict(dict)

        def project(obj):
            try:
                return __project_cache[obj.owner][obj.category]
            except KeyError:
                project, created = models.Project.objects.get_or_create(
                    name=obj.category, owner=obj.owner
                )
                __project_cache[obj.owner][obj.category] = project
                return project

        for pomodoro in models.Pomodoro.objects.filter(owner__username=username, project=None):
            pomodoro.project = project(pomodoro)
            pomodoro.save(update_fields=["project"])

        for favorite in models.Favorite.objects.filter(owner__username=username, project=None):
            favorite.project = project(favorite)
            favorite.save(update_fields=["project"])
