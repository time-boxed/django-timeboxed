import datetime

from django.db import models


class Pomodoro(models.Model):
    created = models.DateTimeField(default=datetime.datetime.now)
    duration = models.IntegerField()
    title = models.CharField(max_length=32)
    category = models.CharField(max_length=32, blank=True)
    owner = models.ForeignKey('auth.User', related_name='pomodoros')

    @property
    def completed(self):
        return self.created + datetime.timedelta(minutes=self.duration)

    def __str__(self):
        return '{}:{}'.format(self.created, self.title)

    class Meta:
        ordering = ('-created',)


class Favorite(models.Model):
    duration = models.IntegerField()
    title = models.CharField(max_length=32)
    category = models.CharField(max_length=32, blank=True)
    owner = models.ForeignKey('auth.User', related_name='favorite')
