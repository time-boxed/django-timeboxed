import logging

from . import models, tasks

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger(__name__)


def queue(owner, driver=None, eta=None, id=None, **kwargs):
    if isinstance(owner, str):
        owner = get_user_model().objects.get(username=owner)

    # If we get a relative URL, make sure we make it a full link
    if "url" in kwargs:
        if kwargs["url"].startswith("/"):
            site = get_current_site(None)
            kwargs["url"] = "https://" + site.domain + kwargs["url"]

    # Start with our default filters
    qs = models.Notification.objects.filter(
        owner=owner,
        enabled=True,
    )
    # if we want to only send using a specific driver
    if driver:
        qs = qs.filter(type=driver)

    for notifier in qs:
        kwargs["pk"] = notifier.pk
        tasks.send_notification.apply_async(
            kwargs=kwargs,
            eta=eta,
        )


def dequeue(id: str, owner):
    if isinstance(owner, str):
        owner = get_user_model().objects.get(username=owner)
    logger.warning("Not yet implemented: %s %s", id, owner)
