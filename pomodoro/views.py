import datetime
import logging

from icalendar import Calendar, Event

from pomodoro import __homepage__, __version__, forms, models

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

try:
    from rest_framework.authtoken.models import Token
except ImportError:
    pass

logger = logging.getLogger(__name__)


class Index(LoginRequiredMixin, FormView):
    template_name = 'pomodoro/index.html'
    form_class = forms.PomodoroForm

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['pomodoro'] = models.Pomodoro.objects\
            .filter(owner=self.request.user).latest('start')
        context['now'] = timezone.now().replace(microsecond=0)
        context['active'] = context['pomodoro'].end > context['now']
        context['diff'] = context['now'] - context['pomodoro'].end

        if context['active']:
            context['hilite'] = 'success'
        elif context['diff'].total_seconds() < 5 * 60 * 60:
            context['hilite'] = 'warning'
        else:
            context['hilite'] = 'danger'

        context['today'] = timezone.localtime(context['now'])\
            .replace(minute=0, hour=0, second=0)

        context['yesterday'] = context['today'] - datetime.timedelta(days=1)
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
            models.Pomodoro.objects.create(**data)
            return redirect(reverse('pomodoro:dashboard'))
        else:
            if 'plus-five' in request.POST:
                pomodoro = models.Pomodoro.objects.latest('start')
                pomodoro.end += datetime.timedelta(minutes=5)
                pomodoro.save()
                return redirect(reverse('pomodoro:dashboard'))

            if 'stop' in request.POST:
                pomodoro = models.Pomodoro.objects.latest('start')
                pomodoro.end = timezone.now().replace(microsecond=0)
                pomodoro.save()
                return redirect(reverse('pomodoro:dashboard'))

            return self.form_invalid(form)


class Favorite(LoginRequiredMixin, View):
    def post(self, request, pk):
        pomodoro = models.Pomodoro.objects\
            .filter(owner=self.request.user).latest('start')
        now = timezone.now().replace(microsecond=0)
        favorite = get_object_or_404(models.Favorite, pk=pk)

        if pomodoro.end > now:
            messages.warning(request, 'Active Pomodoro')
            return redirect(reverse('pomodoro:dashboard'))

        pomodoro = favorite.start(now)
        messages.warning(request, 'Starting Pomodoro {}'.format(pomodoro.title))
        return redirect(reverse('pomodoro:dashboard'))


class FavoriteList(LoginRequiredMixin, ListView):
    model = models.Favorite

    def get_queryset(self):
        print(dir(self))
        return self.model.objects.filter(owner=self.request.user)


class PomodoroHistory(LoginRequiredMixin, ListView):
    model = models.Pomodoro

    def get_queryset(self):
        # TODO: May need to check timezone here
        if self.kwargs.get('date'):
            self.today = timezone.make_aware(
                datetime.datetime.strptime(self.kwargs['date'], '%Y%m%d')
            )
        else:
            self.today = timezone.now()
        self.start = self.today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = self.start + datetime.timedelta(days=1)

        return self.model.objects\
            .filter(start__gte=self.start)\
            .filter(end__lte=end)\
            .filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(PomodoroHistory, self).get_context_data(**kwargs)
        context['today'] = timezone.now()
        context['date'] = self.start
        context['date_prev'] = self.start - datetime.timedelta(days=1)
        next = self.start + datetime.timedelta(days=1)
        if next < context['today']:
            context['date_next'] = next

        return context


class PomodoroCalendarView(View):
    limit = 14

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
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
        cal.add('X-ORIGINAL-URL', request.build_absolute_uri(reverse('pomodoro:calendar')))
        cal.add('X-GENERATOR', __homepage__)
        cal.add('X-GENERATOR-VERSION', __version__)

        # Query today based on the local timezone then strip the timestamps to set it to 00:00
        today = timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)
        query = today - datetime.timedelta(days=self.limit)
        pomodoros = models.Pomodoro.objects.order_by('-start').filter(
            owner=request.user,
            start__gte=query,
        )

        for pomodoro in pomodoros:
            event = Event()
            event.add('summary', '{0} #{1}'.format(pomodoro.title, pomodoro.category))
            event.add('dtstart', pomodoro.start)
            event.add('dtend', pomodoro.end)
            event.add('url', request.build_absolute_uri(pomodoro.get_absolute_url()))
            event['uid'] = pomodoro.id
            cal.add_component(event)

        return HttpResponse(
            content=cal.to_ical(),
            content_type='text/plain; charset=utf-8'
        )


class PomodoroDetailView(UserPassesTestMixin, DetailView):
    model = models.Pomodoro

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        return self.get_object().owner == self.request.user

