from pomodoro import views

from django.urls import path, re_path

app_name = "pomodoro"
urlpatterns = [
    re_path(r"^history/?(?P<date>\w+)?$", views.PomodoroHistory.as_view(), name="pomodoro-list"),
    path("pomodoro/<int:pk>", views.PomodoroDetailView.as_view(), name="pomodoro-detail"),
    path("favorite/<int:pk>", views.FavoriteDetail.as_view(), name="favorite-detail"),
    path("favorite", views.FavoriteList.as_view(), name="favorite-list"),
    path("projects", views.ProjectList.as_view(), name="project-list"),
    path("projects/<pk>", views.ProjectDetail.as_view(), name="project-detail"),
    path("", views.Index.as_view(), name="dashboard"),
    path("share", views.ShareList.as_view(), name="share-list"),
    path("share/<pk>.ics", views.ShareCalendar.as_view(), name="share-calendar"),
]
