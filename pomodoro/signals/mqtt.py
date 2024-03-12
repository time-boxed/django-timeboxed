import logging

from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver
from dmqtt.shortcuts import single

from pomodoro import models, serializers

logger = logging.getLogger(__name__)


@shared_task
def most_recent_pomodoro(owner_id):
    pomodoro = models.Pomodoro.objects.filter(owner_id=owner_id).latest("end")
    topic = "pomodoro/%s/recent" % pomodoro.owner.username
    data = serializers.PomodoroSerializer(pomodoro).data

    single(topic=topic, json=data, retain=True)


@receiver(post_save, sender="pomodoro.Pomodoro")
def most_recent_pomodoro_signal(instance, **kwargs):
    most_recent_pomodoro.delay(owner_id=instance.owner_id)
