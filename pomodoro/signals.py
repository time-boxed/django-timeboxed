import logging

from . import models, tasks

import django.utils.timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="pomodoro.Pomodoro")
def legacy_category(sender, instance, **kwargs):
    if not instance.pk:  # Creating a new instance
        if instance.category:  # and there's a category name
            if not instance.project:  # And there is no project
                instance.project, _ = models.Project.objects.get_or_create(
                    name=instance.category, owner=instance.owner
                )
                logger.info(
                    "Automatically added project %s to %s", instance.project, instance
                )


@receiver(post_save, sender="pomodoro.Pomodoro")
def schedule_notification(sender, instance, created, **kwargs):
    if created is False:
        logger.debug("Skipping notification for modified pomodoro")
        return

    # Skip pomodoro's that are less than 2 minutes long
    if instance.duration.total_seconds() <= 120:
        logger.debug("Skipping notification for short pomodoro")
        return

    now = django.utils.timezone.now()

    if instance.end < now:
        logger.debug("Skipping notification for past pomodoro")
        return

    logger.debug("Queuring notification for %s", instance)
    tasks.send_notification.s(instance.id).apply_async(eta=instance.end)


@receiver(post_save, sender="pomodoro.Pomodoro")
def refresh_count_from_pomodoro(sender, instance, **kwargs):
    tasks.refresh_favorite.delay(category=instance.category, owner_id=instance.owner_id)
    if instance.project_id:
        tasks.refresh_project.delay(pk=instance.project_id)
    tasks.most_recent_pomodoro.delay(owner_id=instance.owner_id)
