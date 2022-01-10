import collections
import datetime
from urllib.parse import urlencode

from django import template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()


@register.filter
def project_report(pomodoro_list):
    projects = collections.defaultdict(datetime.timedelta)
    for pomodoro in pomodoro_list:
        projects[pomodoro.project] += pomodoro.end - pomodoro.start
    for project in projects:
        yield project, projects[project]


@register.simple_tag
def range_qs(**kwargs):
    for key, dt in kwargs.items():
        if isinstance(dt, datetime.date):
            dt = datetime.datetime(dt.year, dt.month, dt.day)
        kwargs[key] = dt.astimezone().isoformat()
    return urlencode(kwargs)


@register.simple_tag
def breadcrumb(instance=None, active=None):
    from pomodoro import models

    def dates(dt: datetime.datetime):
        yield reverse("pomodoro:pomodoro-year", args=(dt.year,)), dt.year
        yield reverse("pomodoro:pomodoro-month", args=(dt.year, dt.month)), dt.month
        yield reverse("pomodoro:pomodoro-day", args=(dt.year, dt.month, dt.day)), dt.day

    def generator():
        yield reverse("pomodoro:dashboard"), _("Home")
        if isinstance(instance, models.Pomodoro):
            yield from dates(instance.start)
            yield instance.get_absolute_url(), instance.title
        if isinstance(instance, models.Project):
            yield reverse("pomodoro:project-list"), _("Projects")
            yield instance.get_absolute_url(), instance.name
        if instance == "Projects":
            yield reverse("pomodoro:project-list"), _("Projects")
        if instance == "Favorites":
            yield reverse("pomodoro:favorite-list"), _("Favorites")
        if instance == "Shares":
            yield reverse("pomodoro:share-list"), _("Shares")

    def to_tag():
        yield '<ol class="breadcrumb">'
        for href, text in generator():
            yield format_html(
                '<li class="breadcrumb-item"><a href="{}">{}</a></li>',
                mark_safe(href),
                text,
            )
        if active:
            yield format_html('<li class="breadcrumb-item active">{}</li>', _(active))
        yield "</ol>"

    return mark_safe("".join(to_tag()))
