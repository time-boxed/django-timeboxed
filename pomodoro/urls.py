from django.conf.urls import patterns, url

import pomodoro.views

urlpatterns = patterns(
    '',
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view()),
    url(r'^chart$', pomodoro.views.ChartView.as_view()),
)
