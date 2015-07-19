import pomodoro.views
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^calendar$', pomodoro.views.PomodoroCalendarView.as_view()),
    url(r'^chart$', pomodoro.views.ChartView.as_view()),
)
