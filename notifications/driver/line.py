from zakka.http import client

# https://notify-bot.line.me/doc/en/


class Line:
    def __init__(self, config):
        self.key = config.key

    def send(self, title, body, **kwargs):
        message = title
        message += "\n"
        message += body
        if "url" in kwargs:
            message += "\n"
            message += kwargs["url"]

        client.post(
            "https://notify-api.line.me/api/notify",
            data={"message": message.strip()},
            headers={"Authorization": f"Bearer {self.key}"},
        ).raise_for_status()
