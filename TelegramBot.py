import requests
from config import TG_CONFIG


class TGBot:
    def __init__(self):
        self.conf = TG_CONFIG

    def sendMessage(self, msg: str):
        method = "sendMessage"
        if len(msg) > 0:
            r = requests.post(
                self.conf["client"] + method,
                data={"chat_id": self.conf["channel_id"], "text": msg},
            )
            if r.status_code != 200:
                raise Exception(r.text)
