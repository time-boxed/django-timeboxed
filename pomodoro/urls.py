from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
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
    if not request.user.logged_in():
        return {}
    return {
        'Pomodoro': {
            'Bar Chart': reverse('%s:bar'%namespace),
            'Pie Chart': reverse('%s:pie'%namespace),
            'Calendar': reverse('%s:calendar'%namespace),
            'Line Chart': reverse('%s:line'%namespace),
        }
    }
