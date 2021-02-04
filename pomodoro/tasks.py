import logging

from celery import shared_task

from pomodoro import models

logger = logging.getLogger(__name__)


@shared_task
def refresh_favorite(**kwargs):
    for favorite in models.Favorite.objects.filter(**kwargs):
        favorite.refresh()


@shared_task
def refresh_project(pk):
    models.Project.objects.get(pk=pk).refresh()


@shared_task
def send_notification(pomodoro_id):
    try:
        pomodoro = models.Pomodoro.objects.get(pk=pomodoro_id)
    except models.Pomodoro.DoesNotExist:
        logger.debug("Skipping missing pomodoro")
        return

    for notification in models.Notification.objects.filter(owner=pomodoro.owner):
        notification.driver.send(pomodoro)


@shared_task
def most_recent_pomodoro(owner_id):
    try:
        driver = models.Notification.drivers["mqtt"]()
    except ImportError:
        return
    else:
        pomodoro = models.Pomodoro.objects.filter(owner_id=owner_id).latest("end")
        driver.send(pomodoro)
