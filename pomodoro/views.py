import sqlite3
import datetime
import logging

from django.http import HttpResponse
from django.views.generic.base import View
from django.conf import settings

from icalendar import Calendar, Event
import pytz


NSTIMEINTERVAL = 978307200

logger = logging.getLogger(__name__)


class PomodoroCalendarView(View):
    database = None
    limit = 10
    format = '{0}'

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        conn = sqlite3.connect(settings.DATABASES[self.database]['NAME'])
        c = conn.cursor()

        logger.info('Reading %d entries from %s', self.limit, settings.DATABASES[self.database]['NAME'])
        print 'Reading {0} entries from {1}'.format(self.limit, settings.DATABASES[self.database]['NAME'])
        c.execute('SELECT Z_PK, ZWHEN, ZDURATIONMINUTES, ZNAME FROM ZPOMODOROS ORDER BY ZWHEN DESC LIMIT ?', (self.limit, ))

        for zpk, zwhen, zminutes, zname in c.fetchall():
            seconds = zminutes * 60
            start = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL - seconds, pytz.utc)
            end = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL, pytz.utc)

            event = Event()
            event.add('summary', self.format.format(zname, zminutes))
            event.add('dtstart', start)
            event.add('dtend', end)
            event['uid'] = zpk
            cal.add_component(event)

        return HttpResponse(
            content=cal.to_ical(),
            content_type='text/plain; charset=utf-8'
            )
