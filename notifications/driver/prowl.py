import requests
from django.contrib.sites.shortcuts import get_current_site

# https://www.prowlapp.com/api.php#add


class Prowl:
    endpoint = "https://api.prowlapp.com/publicapi/add"

    def __init__(self, config):
        self.key = config.key

    def send(self, title, body, **kwargs):
        site = get_current_site(None)
        payload = {
            "apikey": self.key,
            "application": kwargs.get("application", site.domain),
            "event": title,
            "description": body,
            "priority": kwargs.get("priority", 0),
        }
        if "url" in kwargs:
            payload["url"] = kwargs["url"]

        requests.post(self.endpoint, data=payload).raise_for_status()
