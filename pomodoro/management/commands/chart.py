import time
import datetime
import collections

import pytz

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections


from pomodoro.views import NSTIMEINTERVAL


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            database = args[0]
        except:
            raise CommandError('Missing path to pomodoro file')

        hours = 9
        minutes = hours * 60

        # Get midnight today (in the current timezone) as our query point
        today = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)) \
            .replace(hour=0, minute=0, second=0, microsecond=0)# \
        today = time.mktime(today.timetuple()) - NSTIMEINTERVAL

        c = connections[database].cursor()
        c.execute('SELECT Z_PK, cast(ZWHEN as integer), ZDURATIONMINUTES, ZNAME FROM ZPOMODOROS WHERE ZWHEN > %s ORDER BY ZWHEN DESC', [today])

        buckets = collections.defaultdict(int)
        buckets['Unknown'] = minutes
        for zpk, zwhen, zminutes, zname in c.fetchall():
            buckets[zname] += zminutes
            buckets['Unknown'] -= zminutes

        print 'Breakdown for {0} hours'.format(hours)
        print '-' * 80
        for key, value in sorted(buckets.items(), key=lambda x: x[1], reverse=True):
            print u'{hours:0>2}:{minutes:0>2} {percent:>6.2%} {pomodoro}'.format(
                pomodoro=key,
                hours=value / 60,
                minutes=value % 60,
                percent=float(value) / float(minutes),
            )
