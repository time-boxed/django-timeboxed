import json
import uuid

from paho.mqtt.publish import single

from django.conf import settings

from pomodoro import serializers


class MQTT:
    def __init__(self, *args):
        self.client_id = self.domain + "-%d" % uuid.uuid4().int

    def send(self, pomodoro):
        data = serializers.PomodoroSerializer(pomodoro).data
        self.publish("pomodoro/%s/recent" % pomodoro.owner.username, data)

    def publish(self, topic, data, retain=True):
        single(
            topic=topic,
            payload=json.dumps(data).encode("utf8"),
            retain=retain,
            client_id=self.client_id[:23],
            hostname=settings.MQTT_HOST,
            port=settings.MQTT_PORT,
            auth={"username": settings.MQTT_USER, "password": settings.MQTT_PASS},
        )
