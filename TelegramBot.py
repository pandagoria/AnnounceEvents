import requests
import json
from config.tg_config import TG_CONFIG


class TGBot:
    def __init__(self, msg: dict = None):
        self.conf = TG_CONFIG
        self.msgs = msg
        if self.msgs is None:
            with open("message.json") as f:
                self.msgs = json.load(f)

    def sendMassage(self):
        method = "sendMessage"
        for msg in self.msgs.values():
            if len(msg) > 0:
                r = requests.post(
                    self.conf["client"] + method,
                    data={"chat_id": self.conf["channel_id"], "text": msg},
                )
                if r.status_code != 200:
                    raise Exception(r.text)


if __name__ == "__main__":
    bot = TGBot()
    bot.sendMassage()
