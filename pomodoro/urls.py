import pomodoro.views

from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

urlpatterns = [
    url(r'^$', pomodoro.views.Dashboard.as_view(), name='dashboard'),
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view(), name='calendar'),
]


def subnav(namespace, request):
    if not request.user.is_authenticated():
        return {}
    return {
        'Pomodoro': [
            (_('calendar'), reverse(namespace + ':calendar')),
        ]
    }
