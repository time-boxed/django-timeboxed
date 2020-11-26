import collections
import datetime

from django import template
from django.shortcuts import resolve_url
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


@register.simple_tag(takes_context=True)
def dateurl(context, to, dt):
    # TODO: Rather messy
    return resolve_url(to, **{key: getattr(dt, key) for key in context["kwargs"]})


@register.filter
def isoformat(dt, timespec="seconds"):
    return dt.isoformat(timespec=timespec)


@register.simple_tag
def breadcrumb(instance=None, active=None):
    from pomodoro import models

    def dates(dt):
        yield reverse("pomodoro:pomodoro-list", args=(dt.year,)), dt.year
        yield reverse("pomodoro:pomodoro-list", args=(dt.year, dt.month),), dt.month
        yield reverse(
            "pomodoro:pomodoro-list", args=(dt.year, dt.month, dt.day,),
        ), dt.day

    def generator():
        yield reverse("pomodoro:dashboard"), _("home")
        if isinstance(instance, models.Pomodoro):
            yield from dates(instance.start)
            yield instance.get_absolute_url(), instance.title

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
