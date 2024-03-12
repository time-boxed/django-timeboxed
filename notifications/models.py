import logging

try:
    from importlib_metadata import entry_points
except ImportError:
    from importlib.metadata import entry_points

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class Notification(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=32)
    key = models.CharField(max_length=256)
    enabled = models.BooleanField(default=True)

    drivers = {ep.name: ep.load() for ep in entry_points(group="pomodoro.notification")}

    @property
    def driver(self):
        try:
            return self.drivers[self.type](self)
        except Exception:
            logger.exception("Error with driver %s", self.type)
