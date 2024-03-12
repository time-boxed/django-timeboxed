import calendar
import datetime
import logging

import icalendar
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    View,
    dates,
)

from pomodoro import forms, mixins, models

logger = logging.getLogger(__name__)


class Index(LoginRequiredMixin, UpdateView):
    template_name = "pomodoro/index.html"
    form_class = forms.PomodoroForm

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.POST:
            return self.request.POST[REDIRECT_FIELD_NAME]
        return reverse("pomodoro:dashboard")

    def get_object(self):
        return models.Pomodoro.objects.filter(owner=self.request.user).latest("start")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now().replace(microsecond=0)
        context["active"] = context["pomodoro"].end > context["now"]
        return context

    def form_valid(self, form):
        data = form.clean()
        data["owner"] = self.request.user
        data["start"] = timezone.now()
        data["end"] = data["start"] + datetime.timedelta(minutes=data.pop("duration"))
        models.Pomodoro.objects.create(**data)
        return redirect(self.get_success_url())

    def post(self, request):
        if "extend" in self.request.POST:
            pomodoro = self.get_object()
            pomodoro.end += datetime.timedelta(minutes=int(self.request.POST["extend"]))
            pomodoro.save(update_fields=["end"])
            return redirect(self.get_success_url())

        if "stop" in self.request.POST:
            pomodoro = self.get_object()
            pomodoro.end = timezone.now().replace(microsecond=0)
            pomodoro.save(update_fields=["end"])
            pomodoro.save()
            return redirect(self.get_success_url())
        return super().post(self, request)


class HistoryRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        today = timezone.localdate()
        return reverse(
            "pomodoro:pomodoro-day",
            kwargs={
                "year": today.year,
                "month": today.month,
                "day": today.day,
            },
        )


class ProjectList(LoginRequiredMixin, ListView):
    model = models.Project

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


class ProjectUpdate(mixins.OwnerRequiredMixin, UpdateView):
    model = models.Project
    fields = [
        "name",
        "color",
        "url",
        "memo",
        "active",
    ]


class ProjectDetail(mixins.OwnerRequiredMixin, mixins.DateFilterMixin, DetailView):
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(
            self.get_date_qs(context["object"].pomodoro_set.order_by("-start")), 25
        )
        context["paginator"] = paginator
        context["page_obj"] = paginator.get_page(self.request.GET.get("page") or 1)
        return context


class FavoriteDetail(mixins.OwnerRequiredMixin, mixins.DateFilterMixin, DetailView):
    model = models.Favorite

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.POST:
            return self.request.POST[REDIRECT_FIELD_NAME]
        return reverse("pomodoro:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(
            self.get_date_qs(context["object"].pomodoro_set.order_by("-start")), 25
        )
        context["paginator"] = paginator
        context["page_obj"] = paginator.get_page(self.request.GET.get("page") or 1)
        return context

    def post(self, request, pk):
        pomodoro = models.Pomodoro.objects.filter(owner=self.request.user).latest("start")
        now = timezone.now().replace(microsecond=0)

        favorite = get_object_or_404(models.Favorite, pk=pk)

        if pomodoro.end > now:
            messages.warning(request, "There is already an Active Pomodoro")
            return redirect(self.get_success_url())

        pomodoro = favorite.start(now)
        messages.warning(request, f"Starting Pomodoro {pomodoro.title}")
        return redirect(self.get_success_url())


class FavoriteList(LoginRequiredMixin, ListView):
    model = models.Favorite

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user).prefetch_related(
            "owner", "project"
        )


class PomodoroArchiveView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("pomodoro:pomodoro-year", kwargs={"year": timezone.now().year})


class PomodoroArchiveOptions(LoginRequiredMixin):
    allow_empty = True
    model = models.Pomodoro
    make_object_list = True
    allow_future = True
    date_field = "start"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        return context

    def get_dated_queryset(self, **kwargs):
        return (
            self.model.objects.filter(start__gte=kwargs["start__gte"])
            .filter(end__lte=kwargs["start__lt"])
            .filter(owner=self.request.user)
            .prefetch_related("project")
        )


class PomodoroYearView(PomodoroArchiveOptions, dates.YearArchiveView):
    dtfmt = "Y"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["this_year"] = [
            datetime.date(self.kwargs["year"], month, 1) for month in range(1, 13)
        ]
        return context


class PomodoroMonthView(PomodoroArchiveOptions, dates.MonthArchiveView):
    month_format = "%m"
    dtfmt = "N Y"

    def get_context_data(self, **kwargs):
        cal = calendar.Calendar()
        context = super().get_context_data(**kwargs)
        context["this_month"] = datetime.date(self.kwargs["year"], self.kwargs["month"], 1)
        context["calendar"] = cal.monthdatescalendar(self.kwargs["year"], self.kwargs["month"])
        return context


class PomodoroDateView(PomodoroArchiveOptions, dates.DayArchiveView):
    month_format = "%m"


class PomodoroDetailView(mixins.OwnerRequiredMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    model = models.Pomodoro
    form_class = forms.PomodoroEdit


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
            start__gte=share.last_accessed - datetime.timedelta(days=30),
        ).prefetch_related("project"):
            event = icalendar.Event()
            url = request.build_absolute_uri(pomodoro.get_absolute_url())
            event.add("uid", pomodoro.pk)
            event.add("url", url)

            if pomodoro.project:
                event.add("summary", pomodoro.title + " #" + pomodoro.project.name)
            elif pomodoro.category:
                event.add("summary", pomodoro.title + " #" + pomodoro.title)
            else:
                event.add("summary", pomodoro.title)

            event.add("categories", [pomodoro.category])
            event.add("description", pomodoro.memo)
            event.add("dtstart", pomodoro.start)
            event.add("dtend", pomodoro.end)
            cal.add_component(event)

        return HttpResponse(cal.to_ical(), content_type="text/plain")
