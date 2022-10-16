import logging

from . import models, tasks

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def queue(owner, driver=None, eta=None, **kwargs):
    if isinstance(owner, str):
        owner = get_user_model().objects.get(username=owner)

    qs = models.Notification.objects.filter(owner=owner)
    if driver:
        qs = qs.filter(driver=driver)

    for notifier in qs:
        kwargs["driver"] = notifier.driver
        tasks.send_notification.apply_async(
            kwargs=kwargs,
            eta=eta,
        )


def dequeue(id: str, owner):
    if isinstance(owner, str):
        owner = get_user_model().objects.get(username=owner)
    logger.warning("Not yet implemented: %s %s", id, owner)
