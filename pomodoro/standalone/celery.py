from __future__ import absolute_import

import logging

import celery

from django.apps import apps
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)

app = celery.Celery("pomodoro")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")
# https://stackoverflow.com/a/38628748/622650
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
