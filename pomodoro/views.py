import datetime
import logging

from icalendar import Calendar, Event

from pomodoro import __homepage__, __version__, forms
from pomodoro.models import Pomodoro

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.edit import FormView

try:
    from rest_framework.authtoken.models import Token
except ImportError:
    pass

logger = logging.getLogger(__name__)


class Dashboard(FormView):
    template_name = 'pomodoro/dashboard.html'
    form_class = forms.PomodoroForm

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context['pomodoro'] = Pomodoro.objects.latest('start')
        context['now'] = timezone.now()
        context['active'] = context['pomodoro'].end > context['now']
        context['hilite'] = 'success' if context['active'] else 'warning'
        context['today'] = timezone.localtime(timezone.now())\
            .replace(minute=0, hour=0, second=0, microsecond=0)
        context['pomodoro_set'] = Pomodoro.objects.filter(end__gte=context['today'])
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.clean()
            data['owner'] = request.user
            data['start'] = timezone.now()
            if 'pomodoro' in request.POST:
                data['end'] = data['start'] + datetime.timedelta(minutes=25)
            if 'hour' in request.POST:
                data['end'] = data['start'] + datetime.timedelta(hours=1)
            Pomodoro.objects.create(**data)
            return redirect(reverse('pomodoro:dashboard'))
        else:
            if 'plus-five' in request.POST:
                pomodoro = Pomodoro.objects.latest('start')
                pomodoro.end += datetime.timedelta(minutes=5)
                pomodoro.save()
                return redirect(reverse('pomodoro:dashboard'))

            if 'stop' in request.POST:
                pomodoro = Pomodoro.objects.latest('start')
                pomodoro.end = timezone.now()
                pomodoro.save()
                return redirect(reverse('pomodoro:dashboard'))

            return self.form_invalid(form)


class PomodoroCalendarView(View):
    limit = 14

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            try:
                token = Token.objects.select_related('user').get(key=request.GET.get('token'))
                if token:
                    request.user = token.user
                else:
                    return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
            except Exception:
                logger.error('Invalid Token')
                return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        cal = Calendar()
        cal.add('prodid', '-//Pomodoro Calendar//')
        cal.add('version', '2.0')
        cal.add('X-WR-CALNAME', 'Pomodoro for {0}'.format(request.user.username))
        cal.add('X-ORIGINAL-URL', request.build_absolute_uri())
        cal.add('X-GENERATOR', __homepage__)
        cal.add('X-GENERATOR-VERSION', __version__)

        # Query today based on the local timezone then strip the timestamps to set it to 00:00
        today = timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)
        query = today - datetime.timedelta(days=self.limit)
        pomodoros = Pomodoro.objects.order_by('-start').filter(
            owner=request.user,
            start__gte=query,
        )

        for pomodoro in pomodoros:
            event = Event()
            event.add('summary', '{0} #{1}'.format(pomodoro.title, pomodoro.category))
            event.add('dtstart', pomodoro.start)
            event.add('dtend', pomodoro.end)
            event['uid'] = pomodoro.id
            cal.add_component(event)

        return HttpResponse(
            content=cal.to_ical(),
            content_type='text/plain; charset=utf-8'
        )
