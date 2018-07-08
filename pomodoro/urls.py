from pomodoro import views

from django.urls import path

app_name = 'pomodoro'
urlpatterns = [
    path('calendar', views.PomodoroCalendarView.as_view(), name='calendar'),
    path('history/<date>', views.PomodoroHistory.as_view(), name='history'),
    path('pomodoro/<int:pk>', views.PomodoroDetailView.as_view(), name='pomodoro-detail'),
    path('favorite/<int:pk>', views.Favorite.as_view(), name='favorite'),
    path('', views.Index.as_view(), name='dashboard'),
]
