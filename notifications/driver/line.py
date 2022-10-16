import requests

from django.contrib.sites.shortcuts import get_current_site


class Line:
    def __init__(self, config):
        self.key = config.key

    def send(self, pomodoro):
        requests.post(
            "https://notify-api.line.me/api/notify",
            data={
                "message": "{} - {} - {}\n{}{}".format(
                    pomodoro.title,
                    pomodoro.category,
                    pomodoro.duration,
                    get_current_site(None).domain,
                    pomodoro.get_absolute_url(),
                )
            },
            headers={"Authorization": "Bearer {}".format(self.key)},
        ).raise_for_status()
