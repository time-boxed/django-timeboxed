import json
import logging

import requests
from celery import shared_task

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from pomodoro import models, serializers

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = False

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
    if mqtt is False:
        return

    pomodoro = models.Pomodoro.objects.filter(owner_id=owner_id).latest("end")
    data = serializers.PomodoroSerializer(pomodoro).data
    data["html_url"] = "https://" + get_current_site(None) + pomodoro.get_absolute_url()
    publish("pomodoro/%s/recent" % pomodoro.owner.username, data)


@shared_task
def publish(topic, data, retain=True):
    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USER, password=settings.MQTT_PASS)
    client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
    # client.tls_set('/etc/ssl/certs/ca-bundle.trust.crt', tls_version=2)
    client.publish(topic, json.dumps(data).encode("utf8"), retain=retain)
