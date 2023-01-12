import logging

from celery import shared_task

from django.db.models.signals import post_save
from django.dispatch import receiver

from pomodoro import models

logger = logging.getLogger(__name__)


@shared_task
def refresh_favorite(**kwargs):
    for favorite in models.Favorite.objects.filter(**kwargs):
        favorite.refresh()


@shared_task
def refresh_project(pk):
    models.Project.objects.get(pk=pk).refresh()


@receiver(post_save, sender="pomodoro.Pomodoro")
def refresh_count_from_pomodoro(instance, raw, **kwargs):
    if raw:
        return
    refresh_favorite.delay(owner_id=instance.owner_id)
    if instance.project_id:
        refresh_project.delay(pk=instance.project_id)
