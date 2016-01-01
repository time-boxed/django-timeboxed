import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Pomodoro(models.Model):
    created = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('start time'))
    duration = models.IntegerField(verbose_name=_('duration'))
    title = models.CharField(max_length=32, verbose_name=_('title'))
    category = models.CharField(max_length=32, blank=True, verbose_name=_('category'))
    owner = models.ForeignKey('auth.User', related_name='pomodoros', verbose_name=_('owner'))

    @property
    def completed(self):
        return self.created + datetime.timedelta(minutes=self.duration)

    def __str__(self):
        return '{}:{}'.format(self.created, self.title)

    class Meta:
        ordering = ('-created',)


class Favorite(models.Model):
    duration = models.IntegerField(verbose_name=_('duration'))
    title = models.CharField(max_length=32, verbose_name=_('title'))
    category = models.CharField(max_length=32, blank=True, verbose_name=_('category'))
    owner = models.ForeignKey('auth.User', related_name='favorite', verbose_name=_('owner'))
