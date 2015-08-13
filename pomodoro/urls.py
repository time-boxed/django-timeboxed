from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import pomodoro.views

urlpatterns = patterns(
    '',
    url(r'^bar', TemplateView.as_view(template_name="barchart.html")),
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view()),
    url(r'^chart$', pomodoro.views.ChartView.as_view()),
    url(r'^line', TemplateView.as_view(template_name="lineplot.html")),
)
