import datetime

import pytz
from django.core.management.base import BaseCommand
from django.db.backends.sqlite3.base import DatabaseWrapper
from icalendar import Calendar, Event
from pomodoro.legacy import NSTIMEINTERVAL


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('inputfile')
        parser.add_argument('--limit', default=100, type=int)

    def handle(self, *args, **options):
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        cursor = DatabaseWrapper(settings_dict={
            'NAME': options['inputfile'],
            'CONN_MAX_AGE': None,
            'OPTIONS': [],
            'AUTOCOMMIT': False,
        }).cursor()

        cursor.execute('SELECT Z_PK, cast(ZWHEN as integer), ZDURATIONMINUTES, ZNAME FROM ZPOMODOROS ORDER BY ZWHEN DESC LIMIT %s', [options['limit']])

        for zpk, zwhen, zminutes, zname in cursor.fetchall():
            seconds = zminutes * 60
            start = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL - seconds, pytz.utc)
            end = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL, pytz.utc)

            event = Event()
            event.add('summary', u'{0}'.format(zname, zminutes))
            event.add('dtstart', start)
            event.add('dtend', end)
            event['uid'] = zpk
            cal.add_component(event)
        print(cal.to_ical())
