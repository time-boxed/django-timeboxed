import datetime
import logging

import pytz
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from icalendar import Calendar, Event

from pomodoro.models import Pomodoro

logger = logging.getLogger(__name__)


class PomodoroCalendarView(View):
    limit = 7

    def get(self, request, *args, **kwargs):
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        today = datetime.datetime.utcnow()
        query = today - datetime.timedelta(days=self.limit)
        pomodoros = Pomodoro.objects.order_by('-created').filter(
            owner=request.user,
            created__gte=query,
        )

        for pomodoro in pomodoros:
            event = Event()
            event.add('summary', pomodoro.title)
            event.add('dtstart', pomodoro.created)
            event.add('dtend', pomodoro.created + datetime.timedelta(minutes=pomodoro.duration))
            event['uid'] = pomodoro.id
            cal.add_component(event)

        return HttpResponse(
            content=cal.to_ical(),
            content_type='text/plain; charset=utf-8'
        )


class ChartView(View):
    def get(self, request):
        hours = 6
        minutes = hours * 60

        buckets = {}

        today = datetime.datetime.utcnow()
        today.replace(tzinfo=pytz.utc)

        return render(request, 'pomodoro_chart.html', {
            'buckets': buckets,
            'hours': hours,
            'total': minutes,
        })
