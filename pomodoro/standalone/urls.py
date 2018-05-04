from rest_framework import routers

import pomodoro.rest as rest

from django.conf.urls import include, url
from django.contrib import admin

router = routers.DefaultRouter(trailing_slash=False)
router.register('favorites', rest.FavoriteViewSet)
router.register('pomodoros', rest.PomodoroViewSet)

urlpatterns = [
    url('', include('pomodoro.urls', namespace='pomodoro')),
    url('', include('social_django.urls', namespace='social')),
    url('', include('django.contrib.auth.urls')),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^admin/', admin.site.urls),
]
