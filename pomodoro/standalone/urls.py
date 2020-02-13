from rest_framework import routers

from django.conf.urls import include, url
from django.contrib import admin

from pomodoro import rest

router = routers.DefaultRouter(trailing_slash=False)
router.register("favorites", rest.FavoriteViewSet)
router.register("pomodoros", rest.PomodoroViewSet)

urlpatterns = [
    url("", include(("pomodoro.urls", "pomodoro"))),
    url("", include("django.contrib.auth.urls")),
    url("api/", include((router.urls, "api"), namespace="api")),
    url("admin/", admin.site.urls),
]
