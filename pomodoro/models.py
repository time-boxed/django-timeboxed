from django.db import models


class Pomodoro(models.Model):
    created = models.DateTimeField(default=True)
    duration = models.IntegerField()
    title = models.TextField()
    category = models.TextField(blank=True)
    owner = models.ForeignKey('auth.User', related_name='pomodoros')

    def __str__(self):
        return '{}:{}'.format(self.created, self.title)

    class Meta:
        ordering = ('-created',)


class Favorite(models.Model):
    duration = models.IntegerField()
    title = models.TextField()
    category = models.TextField(blank=True)
    owner = models.ForeignKey('auth.User', related_name='favorite')
