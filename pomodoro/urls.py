from pomodoro import views

from django.urls import path, re_path

app_name = 'pomodoro'
urlpatterns = [
    re_path(r'^history/?(?P<date>\w+)?$', views.PomodoroHistory.as_view(), name='pomodoro-list'),
    path('pomodoro/<int:pk>', views.PomodoroDetailView.as_view(), name='pomodoro-detail'),
    path('favorite/<int:pk>', views.Favorite.as_view(), name='favorite'),
    path('favorite', views.FavoriteList.as_view(), name='favorite-list'),
    path('', views.Index.as_view(), name='dashboard'),
]
