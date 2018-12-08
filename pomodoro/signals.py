import logging

from pomodoro import models, tasks

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(
    post_save, sender=models.Pomodoro, weak=False, dispatch_uid="signal_pomodoro_jobs"
)
def signal_pomodoro_jobs(sender, instance, **kwargs):
    print("signal_pomodoro_jobs")
    tasks.most_recent_pomodoro.delay(instance.owner.id)
    tasks.refresh_favorite.delay(category=instance.category, owner_id=instance.owner_id)


@receiver(post_save, sender=models.Pomodoro)
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
    tasks.send_notification.s(instance.id).apply_async(eta=instance.end)
