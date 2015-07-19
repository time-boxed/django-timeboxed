import collections
import datetime
import logging

import pytz
from django.conf import settings
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from icalendar import Calendar, Event
from pomodoro.legacy import NSTIMEINTERVAL, PomodoroBucket

logger = logging.getLogger(__name__)


class PomodoroCalendarView(View):
    database = None
    limit = 10
    format = u'{0}'

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        c = connections[self.database].cursor()

        logger.info('Reading %d entries from %s', self.limit, settings.DATABASES[self.database]['NAME'])
        # Cast ZWHEN as int to get around a bug? with django's query
        c.execute('SELECT Z_PK, cast(ZWHEN as integer), ZDURATIONMINUTES, ZNAME FROM ZPOMODOROS ORDER BY ZWHEN DESC LIMIT %s', [self.limit])

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


class ChartView(View):
    database = None

    def get(self, request):
        hours = 6
        minutes = hours * 60

        # Get midnight today (in the current timezone) as our query point
        start = PomodoroBucket.midnight(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)))

        buckets = collections.OrderedDict()
        for pomodoro, total in PomodoroBucket.get(self.database, start, minutes):
            buckets[pomodoro] = {
                'total': total,
                'hours': total / 60,
                'minutes': total % 60,
                'percent': float(total) / float(minutes)
            }

        return render(request, 'pomodoro_chart.html', {
            'buckets': buckets,
            'hours': hours,
            'total': minutes,
        })
