import json
import os

from django.core.management.base import BaseCommand


import paho.mqtt.client as mqtt


class Command(BaseCommand):
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf8")
        try:
            print(msg.topic, json.loads(payload))
        except:
            print(msg.topic, payload)

    def handle(self, **options):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(
            os.environ["MQTT_USER"], password=os.environ["MQTT_PASS"]
        )

        client.connect(os.environ["MQTT_HOST"], 1883, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            pass
