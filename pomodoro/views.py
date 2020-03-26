import datetime
import logging

import icalendar

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from pomodoro import forms, mixins, models

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


class PomodoroDetailView(mixins.OwnerRequiredMixin, DetailView):
    model = models.Pomodoro


class ShareList(LoginRequiredMixin, ListView):
    model = models.Share

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


class ShareCalendar(View):
    def get(self, request, pk):
        share = get_object_or_404(models.Share, pk=pk)
        share.last_accessed = timezone.now()
        share.save(update_fields=["last_accessed"])

        cal = icalendar.Calendar()
        cal.add("prodid", "-//Pomodoro Calendar//")
        cal.add("version", "2.0")
        cal.add("X-ORIGINAL-URL", request.build_absolute_uri())
        cal.add("X-WR-CALNAME", "Calendar Share for %s" % share.owner)

        for pomodoro in models.Pomodoro.objects.filter(
            owner=share.owner,
            start_gte=share.last_accessed - datetime.timedelta(days=14),
        ):
            event = icalendar.Event()
            url = request.build_absolute_uri(pomodoro.get_absolute_url())
            event.add("uid", pomodoro.pk)
            event.add("url", url)
            event.add("categories", [pomodoro.category])
            event.add("description", pomodoro.memo)
            event.add("dtstart", pomodoro.start)
            event.add("dtend", pomodoro.end)
            cal.add_component(event)

        return HttpResponse(cal.to_ical(), content_type="text/plain")
