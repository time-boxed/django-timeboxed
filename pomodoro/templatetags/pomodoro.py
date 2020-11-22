import collections
import datetime

from django import template

register = template.Library()


@register.filter
def project_report(pomodoro_list):
    projects = collections.defaultdict(datetime.timedelta)
    for pomodoro in pomodoro_list:
        projects[pomodoro.project] += pomodoro.end - pomodoro.start
    for project in projects:
        yield project, projects[project]
