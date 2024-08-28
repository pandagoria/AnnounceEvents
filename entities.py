import json


class Config:
    def __init__(self, conf_file: str):
        self.conf_file = conf_file
        with open(conf_file) as fd:
            json_config = json.load(fd)
        for key in json_config:
            setattr(self, key, json_config[key])

    def json_deserialize_to_file(self):
        with open(self.conf_file, "w") as fd:
            json.dump(self.__dict__, fd, indent=4, sort_keys=True)


class Scopes:
    USER_SHOW = "oauth-user-show"
    ONATION_SUBSCRIBE = "oauth-donation-subscribe"
    DONATION_INDEX = "oauth-donation-index"
    CUSTOM_ALERT_STORE = "oauth-custom_alert-store"
    GOAL_SUBSCRIBE = "oauth-goal-subscribe"
    POLL_SUBSCRIBE = "oauth-poll-subscribe"
    ALL_SCOPES = "oauth-user-show oauth-donation-subscribe oauth-donation-index oauth-goal-subscribe oauth-poll-subscribe"


class Channels:
    NEW_DONATION_ALERTS = "$alerts:donation_"
    DONATION_GOALS_UPDATES = "$goals:goal_"
    POLLS_UPDATES = "$polls:poll_"
    ALL_CHANNELS = ["$alerts:donation_", "$goals:goal_", "$polls:poll_"]
