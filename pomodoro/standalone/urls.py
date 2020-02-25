from rest_framework import routers

from django.urls import include, path
from django.contrib import admin

from pomodoro import rest

router = routers.DefaultRouter(trailing_slash=False)
router.register("favorites", rest.FavoriteViewSet)
router.register("pomodoros", rest.PomodoroViewSet)

urlpatterns = [
    path("", include(("pomodoro.urls", "pomodoro"))),
    path("", include("django.contrib.auth.urls")),
    path("grafana/", include(("pomodoro.grafana"), namespace="grafana")),
    path("api/", include((router.urls, "api"), namespace="api")),
    path("admin/", admin.site.urls),
]
