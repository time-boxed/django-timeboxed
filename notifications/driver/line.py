import requests

# https://notify-bot.line.me/doc/en/


class Line:
    def __init__(self, config):
        self.key = config.key

    def send(self, **kwargs):
        message = kwargs.get("title")
        message += "\n"
        message += kwargs.get("body")
        if "url" in kwargs:
            message += "\n"
            message += kwargs["url"]

        requests.post(
            "https://notify-api.line.me/api/notify",
            data={"message": message},
            headers={"Authorization": "Bearer {}".format(self.key)},
        ).raise_for_status()
