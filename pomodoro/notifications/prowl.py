import requests

from django.contrib.sites.shortcuts import get_current_site


class Prowl:
    def __init__(self, config):
        self.key = config.key

    def send(self, pomodoro):
        requests.post(
            "https://api.prowlapp.com/publicapi/add",
            data={
                "apikey": self.key,
                "application": "Pomodoro - {}".format(get_current_site(None)),
                "event": "Pomodoro Complete",
                "url": "https://{}{}".format(
                    get_current_site(None), pomodoro.get_absolute_url()
                ),
                "description": "{} - {} - {}".format(
                    pomodoro.title, pomodoro.category, pomodoro.duration,
                ),
            },
        ).raise_for_status()
