import logging

import requests
from celery import shared_task

from pomodoro import models, serializers, utils

import django.utils.timezone
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import post_save
from django.dispatch import receiver


logger = logging.getLogger(__name__)


@shared_task
def refresh_favorite(**kwargs):
    for favorite in models.Favorite.objects.filter(**kwargs):
        favorite.refresh()


@shared_task
def send_notification(pomodoro_id):
    def prowl(key, pomodoro):
        requests.post('https://api.prowlapp.com/publicapi/add', data={
            'apikey': key,
            'application': 'Pomodoro - {}'.format(get_current_site(None)),
            'event': 'Pomodoro Complete',
            'url': 'https://{}{}'.format(
                get_current_site(None),
                pomodoro.get_absolute_url()),
            'description': '{} - {} - {}'.format(
                pomodoro.title,
                pomodoro.category,
                pomodoro.duration,
            ), 
        }).raise_for_status()

    def line(key, pomodoro):
        requests.post('https://notify-api.line.me/api/notify', data={
            'message': '{} - {} - {}\n{}{}'.format(
                pomodoro.title,
                pomodoro.category,
                pomodoro.duration,
                get_current_site(None),
                pomodoro.get_absolute_url(),
            )
        }, headers={
            'Authorization': 'Bearer {}'.format(key)
        }).raise_for_status()

    pomodoro = models.Pomodoro.objects.get(pk=pomodoro_id)
    for notification in models.Notification.objects.filter(owner=pomodoro.owner):
        if notification.type == 'prowl':
            prowl(notification.key, pomodoro)
        if notification.type == 'line':
            line(notification.key, pomodoro)


@shared_task
def most_recent_pomodoro(owner_id):
    pomodoro = models.Pomodoro.objects.filter(owner_id=owner_id).latest("end")
    utils.publish(
        "pomodoro/{}/recent".format(pomodoro.owner.username),
        json=serializers.PomodoroSerializer(pomodoro).data,
        retain=True,
    )

