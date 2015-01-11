from django.core.management.base import BaseCommand, CommandError

from pomodoro.views import PomodoroCalendarView


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            database = args[0]
        except:
            raise CommandError('Missing path to pomodoro file')

        view = PomodoroCalendarView()
        view.database = database
        view.limit = 250
        response = view.get(None)
        print response.content
