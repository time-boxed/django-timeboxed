import logging

from celery import shared_task

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from pomodoro import models

logger = logging.getLogger(__name__)


@receiver(post_save, sender="pomodoro.Pomodoro")
def schedule_notification(sender, instance, created, **kwargs):
    if created is False:
        logger.debug("Skipping notification for modified pomodoro")
        return

    # Skip pomodoro's that are less than 2 minutes long
    if instance.duration.total_seconds() <= 120:
        logger.debug("Skipping notification for short pomodoro")
        return

    now = timezone.now()

    if instance.end < now:
        logger.debug("Skipping notification for past pomodoro")
        return

    logger.debug("Queuring notification for %s", instance)
    send_notification.s(instance.id).apply_async(eta=instance.end)


@shared_task
def send_notification(pomodoro_id):
    try:
        pomodoro = models.Pomodoro.objects.get(pk=pomodoro_id)
    except models.Pomodoro.DoesNotExist:
        logger.debug("Skipping missing pomodoro")
        return

    for notification in models.Notification.objects.filter(owner=pomodoro.owner):
        notification.driver.send(pomodoro)
