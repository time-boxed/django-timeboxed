import collections
import datetime

from django import template
from django.shortcuts import resolve_url

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

