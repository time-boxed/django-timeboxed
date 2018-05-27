import pomodoro.views

from django.conf.urls import url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

app_name = 'pomodoro'
urlpatterns = [
    url(r'^$', pomodoro.views.Dashboard.as_view(), name='dashboard'),
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view(), name='calendar'),
    url(r'^favorite/(?P<pk>.*)$', pomodoro.views.Favorite.as_view(), name='favorite'),
]


def subnav(namespace, request):
    if not request.user.is_authenticated():
        return {}
    return {
        'Pomodoro': [
            (_('calendar'), reverse(namespace + ':calendar')),
        ]
    }
