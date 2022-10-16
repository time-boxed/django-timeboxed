from celery import shared_task

from . import models


@shared_task
def send_notification(pk, **kwargs):
    notifier = models.Notification.objects.get(pk=pk)
    notifier.driver.send(**kwargs)
