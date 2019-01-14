import datetime

from django.utils.dateparse import parse_datetime
from icalendar import Calendar, Event
from rest_framework import renderers


class CalendarRenderer(renderers.BaseRenderer):
    '''
    Basic iCalendar renderer

    Attempts to render a list of Pomodoro objects (passed from a ViewSet)
    As an iCalendar file
    '''
    media_type = 'text/plain'
    format = 'ics'

    def render(self, data, media_type=None, renderer_context=None):
        cal = Calendar()
        cal.add('prodid', '-//django-pomodoro//kungfudiscomonkey.net//')
        cal.add('version', '2.0')

        # TODO: Need a better way to return when results are empty
        # For example when calls are not authed
        if 'results' not in data:
            return ''

        for pomodoro in data['results']:
            event = Event()
            # TODO: Need to find the original object so that we don't have to convert back and forth
            created = parse_datetime(pomodoro['created'])

            event.add('summary', pomodoro['title'])
            event.add('dtstart', created)
            event.add('dtend', created + datetime.timedelta(minutes=pomodoro['duration']))
            event['uid'] = pomodoro['id']
            cal.add_component(event)

        return cal.to_ical()
