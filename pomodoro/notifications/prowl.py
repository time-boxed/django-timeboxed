import requests

from django.contrib.sites.shortcuts import get_current_site

# https://www.prowlapp.com/api.php#add


class Prowl:
    endpoint = "https://api.prowlapp.com/publicapi/add"

    def __init__(self, config):
        self.key = config.key

    def send(self, pomodoro):
        site = get_current_site(None)
        return self.publish(
            apikey=self.apikey,
            application=f"Pomodoro - {site.domain}",
            event="Pomodoro Complete",
            url=f"https://{site.domain}{pomodoro.get_absolute_url()}",
            description=f"{pomodoro.title} - {pomodoro.category} - {pomodoro.duration}",
        )

    def publish(self, **kwargs):
        kwargs.setdefault("apikey", self.key)
        requests.post(
            self.endpoint,
            data=kwargs,
        ).raise_for_status()
