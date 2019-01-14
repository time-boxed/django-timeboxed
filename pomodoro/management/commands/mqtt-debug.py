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

    def add_arguments(self, parser):
        parser.add_argument("-u", "--user", default=os.environ.get("MQTT_USER"))
        parser.add_argument("-p", "--password", default=os.environ.get("MQTT_PASS"))
        parser.add_argument("--host", default=os.environ.get("MQTT_HOST", "localhost"))
        parser.add_argument(
            "-P", "--port", type=int, default=os.environ.get("MQTT_PORT", 1883)
        )

    def handle(self, **options):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(options["user"], password=options["password"])

        client.connect(options["host"], options["port"], 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            pass
