import pomodoro.views

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^bar', login_required(TemplateView.as_view(template_name="charts/bar.html")), name='bar'),
    url(r'^pie', login_required(TemplateView.as_view(template_name="charts/pie.html")), name='pie'),
    url(r'^today', login_required(TemplateView.as_view(template_name="charts/today.html")), name='today'),
    url(r'^yesterday', login_required(TemplateView.as_view(template_name="charts/yesterday.html")), name='yesterday'),
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view(), name='calendar'),
    url(r'^line', login_required(TemplateView.as_view(template_name="charts/annotation.html")), name='line'),
]


def subnav(namespace, request):
    if not request.user.is_authenticated():
        return {}
    return {
        'Pomodoro': [
            (_('today'), reverse(namespace + ':today')),
            (_('yesterday'), reverse(namespace + ':yesterday')),
            (_('bar chart'), reverse(namespace + ':bar')),
            (_('pie chart'), reverse(namespace + ':pie')),
            (_('line chart'), reverse(namespace + ':line')),
            (_('calendar'), reverse(namespace + ':calendar')),
        ]
    }
