from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from pomodoro import rest

router = routers.DefaultRouter(trailing_slash=False)
router.register("favorites", rest.FavoriteViewSet)
router.register("pomodoros", rest.PomodoroViewSet)
router.register("project", rest.ProjectViewSet)

urlpatterns = [
    path("", include(("pomodoro.urls", "pomodoro"))),
    path("", include("django.contrib.auth.urls")),
    path("grafana/", include(("pomodoro.grafana"), namespace="grafana")),
    path("api/", include((router.urls, "api"), namespace="api")),
    path("admin/", admin.site.urls),
]
