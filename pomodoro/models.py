from django.db import models


class Pomodoro(models.Model):
    created = models.DateTimeField(default=True)
    duration = models.IntegerField()
    title = models.TextField()
    owner = models.ForeignKey('auth.User', related_name='pomodoros')

    class Meta:
        ordering = ('created',)
