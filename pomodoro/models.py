import datetime
import os

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


def _upload_to_path(instance, filename):
    root, ext = os.path.splitext(filename)
    return 'pomodoro/favorites/{}{}'.format(instance.pk, ext)


class Tag(models.Model):
    title = models.CharField(max_length=32, verbose_name=_('title'))
    owner = models.ForeignKey('auth.User', related_name='+', verbose_name=_('owner'), on_delete=models.CASCADE)

    class Meta:
        unique_together = ("title", "owner")
        ordering = ('title',)

    def __str__(self):
        return self.title


class Pomodoro(models.Model):
    start = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('start time'))
    end = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('end time'))

    title = models.CharField(max_length=32, verbose_name=_('title'))
    category = models.CharField(max_length=32, blank=True, verbose_name=_('category'))
    owner = models.ForeignKey('auth.User', related_name='pomodoros', verbose_name=_('owner'), on_delete=models.CASCADE)

    tags = models.ManyToManyField('pomodoro.Tag')

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

    tags = models.ManyToManyField('pomodoro.Tag', related_name='favorite_set')

    class Meta:
        ordering = ('-count',)

    def refresh(self):
        duration = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        self.count = Pomodoro.objects.filter(
            start__gte=duration,
            owner=self.owner,
            title=self.title,
            category=self.category
        ).count()
        self.save()

    def timedelta(self):
        return datetime.timedelta(minutes=self.duration)

    def start(self, ts):
        pomodoro = Pomodoro()
        pomodoro.title = self.title
        pomodoro.category = self.category
        pomodoro.owner = self.owner
        pomodoro.start = ts
        pomodoro.end = ts + datetime.timedelta(minutes=self.duration)
        pomodoro.save()
        return pomodoro


class Notification(models.Model):
    owner = models.ForeignKey('auth.User', related_name='notification', verbose_name=_('owner'), on_delete=models.CASCADE)
    type = models.CharField(max_length=32)
    key = models.CharField(max_length=128)
    enabled = models.BooleanField(default=True)
