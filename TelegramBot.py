import requests
from config import TG_CONFIG


class TGBot:
    def __init__(self):
        self.conf = TG_CONFIG

    def sendMessage(self, msg: str, file_url=None):
        method = "sendMessage"
        if len(msg) > 0:
            if file_url:
                method = "sendPhoto"
                r = requests.post(
                    url=self.conf["client"] + method,
                    data={
                        "chat_id": self.conf["channel_id"],
                        "caption": msg,
                        "photo": file_url,
                    },
                )
            else:
                r = requests.post(
                    self.conf["client"] + method,
                    data={"chat_id": self.conf["channel_id"], "text": msg},
                )
            if r.status_code != 200:
                raise Exception(r.text)
