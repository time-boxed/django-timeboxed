import logging

import requests
from celery import shared_task

from pomodoro import models

import django.utils.timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@shared_task
def send_notification(pomodoro_id):
    def prowl(key, pomodoro):
        requests.post('https://api.prowlapp.com/publicapi/add', data={
            'apikey': key,
            'application': 'Pomodoro',
            'event': 'Pomodoro Complete',
            'description': '{} - {} - {}'.format(
                pomodoro.title,
                pomodoro.category,
                pomodoro.duration,
            ),
        }).raise_for_status()

    pomodoro = models.Pomodoro.objects.get(pk=pomodoro_id)
    for notification in models.Notification.objects.filter(owner=pomodoro.owner):
        if notification.type == 'prowl':
            prowl(notification.key, pomodoro)


@receiver(post_save, sender=models.Pomodoro)
def my_callback(sender, instance, created, **kwargs):
    if created is False:
        logger.debug('Skipping notification for modified pomodoro')
        return

    # Skip pomodoro's that are less than 2 minutes long
    if instance.duration.total_seconds() <= 120:
        logger.debug('Skipping notification for short pomodoro')
        return

    now = django.utils.timezone.now()

    if instance.end < now:
        logger.debug('Skipping notification for past pomodoro')
        return

    logger.debug('Queuring notification for %s', instance)
    send_notification.s(instance.id).apply_async(eta=instance.end)
