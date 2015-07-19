import datetime

import pytz
from pomodoro.models import PomodoroBucket

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            database = args[0]
        except:
            raise CommandError('Missing path to pomodoro file')

        hours = 9
        hours = 6
        minutes = hours * 60

        # Get midnight today (in the current timezone) as our query point
        start = PomodoroBucket.midnight(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))

        buckets = PomodoroBucket.get(database, start, minutes)

        print 'Breakdown for {0} hours'.format(hours)
        print '-' * 80
        for key, value in buckets:
            print u'{hours:0>2}:{minutes:0>2} {percent:>6.2%} {pomodoro}'.format(
                pomodoro=key,
                hours=value / 60,
                minutes=value % 60,
                percent=float(value) / float(minutes),
            )
