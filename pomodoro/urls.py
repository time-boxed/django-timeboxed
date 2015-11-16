from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

import pomodoro.views

urlpatterns = patterns(
    '',
    url(r'^bar', login_required(TemplateView.as_view(template_name="charts/bar.html"))),
    url(r'^pie', login_required(TemplateView.as_view(template_name="charts/pie.html"))),
    url(r'^today', login_required(TemplateView.as_view(template_name="charts/today.html"))),
    url(r'^yesterday', login_required(TemplateView.as_view(template_name="charts/yesterday.html"))),
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view()),
    url(r'^line', login_required(TemplateView.as_view(template_name="charts/annotation.html"))),
)
