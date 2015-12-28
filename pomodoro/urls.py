from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

import pomodoro.views

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
            ('Bar Chart', reverse(namespace + ':bar')),
            ('Pie Chart', reverse(namespace + ':pie')),
            ('Line Chart', reverse(namespace + ':line')),
            ('Calendar', reverse(namespace + ':calendar')),
        ]
    }
