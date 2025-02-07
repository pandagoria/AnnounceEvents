import requests
from config import TG_CONFIG


class TGBot:
    def __init__(self):
        self.conf = TG_CONFIG

    def sendMessage(self, msg: str, file_url=None):
        if len(msg) > 0:
            if method == "sendPhoto":
                r_group = requests.post(
                    url=self.conf["client"] + method,
                    data={
                        "chat_id": self.conf["panda_group"]["channel_id"],
                        "caption": msg,
                        "photo": file_url,
                    },
                )
            else:
                r_group = requests.post(
                    self.conf["client"] + method,
                    data={
                        "chat_id": self.conf["panda_group"]["channel_id"],
                        "text": msg,
                    },
                )
            if r_group.status_code != 200:
                raise Exception(r.text)
