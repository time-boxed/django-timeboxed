import json

import paho.mqtt.client as mqtt

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from pomodoro import serializers


class MQTT:
    def __init__(self, *args):
        pass

    def send(self, pomodoro):
        data = serializers.PomodoroSerializer(pomodoro).data
        data["html_url"] = (
            "https://" + get_current_site(None).domain + pomodoro.get_absolute_url()
        )
        self.publish("pomodoro/%s/recent" % pomodoro.owner.username, data)

    def publish(self, topic, data, retain=True):
        client = mqtt.Client()
        client.username_pw_set(settings.MQTT_USER, password=settings.MQTT_PASS)
        client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
        # client.tls_set('/etc/ssl/certs/ca-bundle.trust.crt', tls_version=2)
        client.publish(topic, json.dumps(data).encode("utf8"), retain=retain)
