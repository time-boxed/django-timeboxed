import datetime
import logging
import os

import pkg_resources

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def _upload_to_path(instance, filename):
    root, ext = os.path.splitext(filename)
    return 'pomodoro/favorites/{}{}'.format(instance.pk, ext)


class Pomodoro(models.Model):
    start = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('start time'))
    end = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('end time'))

    title = models.CharField(max_length=32, verbose_name=_('title'))
    category = models.CharField(max_length=32, blank=True, verbose_name=_('category'))
    owner = models.ForeignKey('auth.User', related_name='pomodoros', verbose_name=_('owner'), on_delete=models.CASCADE)

    url = models.URLField(blank=True, help_text="Optional link")
    memo = models.TextField(blank=True)

    @property
    def duration(self):
        return self.end - self.start
    duration.fget.short_description = _('duration')

    def __str__(self):
        return '{}:{}'.format(self.start, self.title)

    def get_absolute_url(self):
        return reverse('pomodoro:pomodoro-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('-start',)


class Favorite(models.Model):
    duration = models.IntegerField(verbose_name=_('duration'))
    title = models.CharField(max_length=32, verbose_name=_('title'))
    category = models.CharField(max_length=32, blank=True, verbose_name=_('category'))
    owner = models.ForeignKey('auth.User', related_name='favorite', verbose_name=_('owner'), on_delete=models.CASCADE)
    icon = models.ImageField(upload_to=_upload_to_path, blank=True)
    count = models.PositiveIntegerField(default=0)
    url = models.URLField(blank=True)

    class Meta:
        ordering = ('-count',)

    def refresh(self):
        duration = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        self.count = Pomodoro.objects.filter(
            start__gte=duration,
            owner=self.owner,
            title=self.title,
            category=self.category,
        ).count()
        self.save(update_fields=("count",))

    def timedelta(self):
        return datetime.timedelta(minutes=self.duration)

    def start(self, ts):
        return Pomodoro.objects.create(
            title=self.title,
            category=self.category,
            owner=self.owner,
            start=ts,
            end=ts + datetime.timedelta(minutes=self.duration),
        )


class Notification(models.Model):
    owner = models.ForeignKey(
        "auth.User",
        related_name="+",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=32)
    key = models.CharField(max_length=128)
    enabled = models.BooleanField(default=True)

    drivers = {
        ep.name: ep.load()
        for ep in pkg_resources.iter_entry_points("pomodoro.notification")
    }

    @property
    def driver(self):
        try:
            return self.drivers[self.type](self)
        except Exception:
            logger.exception("Error with driver %s", self.type)
