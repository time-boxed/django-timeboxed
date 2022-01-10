from django.urls import path

from pomodoro import views

app_name = "pomodoro"
urlpatterns = [
    path("report/", views.PomodoroArchiveView.as_view(), name="pomodoro-list"),
    path("report/<int:year>/", views.PomodoroYearView.as_view(), name="pomodoro-year"),
    path("report/<int:year>/<int:month>/", views.PomodoroMonthView.as_view(), name="pomodoro-month"),
    path("report/<int:year>/<int:month>/<int:day>/", views.PomodoroDateView.as_view(), name="pomodoro-day"),
    path("pomodoro/<int:pk>", views.PomodoroDetailView.as_view(), name="pomodoro-detail"),
    path("favorite/<int:pk>", views.FavoriteDetail.as_view(), name="favorite-detail"),
    path("favorite", views.FavoriteList.as_view(), name="favorite-list"),
    path("projects", views.ProjectList.as_view(), name="project-list"),
    path("projects/<pk>", views.ProjectDetail.as_view(), name="project-detail"),
    path("projects/<pk>/update", views.ProjectUpdate.as_view(), name="project-update"),
    path("", views.Index.as_view(), name="dashboard"),
    path("share", views.ShareList.as_view(), name="share-list"),
    path("share/<pk>.ics", views.ShareCalendar.as_view(), name="share-calendar"),
]
