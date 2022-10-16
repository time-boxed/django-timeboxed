import logging

from notifications.shortcuts import dequeue, queue

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(post_save, sender="pomodoro.Pomodoro")
def schedule_notification(instance, created, **kwargs):
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

    queue(
        id=f"pomodoro:{instance.pk}",
        owner=instance.owner,
        title=instance.title,
        body=f"{instance.title} {instance.duration}",
        url=instance.get_absolute_url(),
        eta=instance.end,
    )


@receiver(post_delete, sender="pomodoro.Pomodoro")
def unschedule_notification(instance, **kwargs):
    dequeue(id=f"pomodoro:{instance.pk}")
