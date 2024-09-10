import logging
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import json
from aiohttp import ClientSession, web, ClientError, WSMsgType, ServerDisconnectedError
import asyncio

from entities import Config

# logging.basicConfig(level=logging.INFO, filename="NEW_LOG.txt")


class TwitchClient:
    def __init__(self, discord_bot=None) -> None:
        self.config = Config("config/twitch_config.json")
        self.auth_session = None
        self.discord_bot = discord_bot
        self.loop = asyncio.get_event_loop()

    def authorize(self) -> None:
        self.auth_session = OAuth2Session(
            self.config.client_id,
            redirect_uri=self.config.redirect_uri,
            scope=self.config.scope,
            token=self.config.token,
        )

        if not self.config.token:
            # Процесс первой авторизации
            authorization_url, _ = self.auth_session.authorization_url(
                self.config.oauth_url + "/authorize"
            )
            print(f"Please go to {authorization_url} and authorize access.")
            authorization_response = input("Enter the full callback URL")
            self.config.token = self.auth_session.fetch_token(
                self.config.oauth_url + "/token",
                verify=False,
                authorization_response=authorization_response,
                client_secret=self.config.client_secret,
                include_client_id=self.config.client_id,
                access_type="authorization_code",
                method="POST",
            )
            logging.info("Token fetched")
            self.config.json_deserialize_to_file()
            logging.info("Token info saved")
        else:
            try:
                # Обновление токена с использованием рефреш токена
                self.config.token = self.auth_session.refresh_token(
                    self.config.oauth_url + "/token",
                    verify=False,
                    refresh_token=self.config.token["refresh_token"],  # unneseccary
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret,
                )
                logging.info("Token refreshed")
                self.config.json_deserialize_to_file()
                logging.info("Token info saved")
            except Exception as e:
                logging.error(f"fatal error when refreshing token: {e}")
                raise

    def get_panda_user_id(self) -> None:
        if self.auth_session is None:
            self.auth_session = OAuth2Session(
                self.config.client_id,
                redirect_uri=self.config.redirect_uri,
                scope=self.config.scope,
                token=self.config.token,
            )
        r = self.auth_session.get(
            self.config.api_url + "/helix/users?login=pandagoria",
            headers={
                "Authorization": "Bearer " + self.config.token["access_token"],
                "Client-Id": self.config.client_id,
            },
        )
        user_data = r.json()
        logging.info(user_data)
        self.config.user_id = user_data["data"][0]["id"]
        self.config.json_deserialize_to_file()

    def get_stream_info(self):
        if self.auth_session is None:
            self.authorize()
        r = self.auth_session.get(
            f"{self.config.api_url}/helix/channels?broadcaster_id={self.config.user_id}",
            headers={
                "Authorization": "Bearer " + self.config.token["access_token"],
                "Client-Id": self.config.client_id,
            },
        )
        stream_data = r.json()["data"][0]
        logging.info(stream_data)
        return stream_data["game_name"], stream_data["title"]

    def events_sub(self, session_id):
        data = {
            "type": self.config.eventsub["eventsubs"],
            "version": "1",
            "condition": {"broadcaster_user_id": self.config.user_id},
            "transport": {"method": "websocket", "session_id": session_id},
        }
        if self.auth_session is None:
            self.authorize()
        r = self.auth_session.post(
            self.config.api_url + "/helix/eventsub/subscriptions",
            headers={
                "Authorization": "Bearer " + self.config.token["access_token"],
                "Content-Type": "application/json",
                "Client-Id": self.config.client_id,
            },
            data=json.dumps(data),
        )
        return r.json()

    async def websocket_session(self):
        async with ClientSession() as session:
            reconnect = False
            while True:
                try:
                    if reconnect is True:
                        await self.run_ws(session, reconnect=True)
                    else:
                        await self.run_ws(session)
                except ClientError as e:
                    logging.warning(f"Reconnecting WS: {e}")
                    reconnect = True
                except ServerDisconnectedError as e:
                    logging.error(f"shiiit: {e}")
                    raise

    async def run_ws(self, session, reconnect=False) -> None:
        async with session.ws_connect(self.config.eventsub["websocket_url"]) as ws:
            res = await ws.receive()
            session_id = json.loads(res.data)["payload"]["session"]["id"]
            logging.info("Connected")
            if not reconnect:
                private_channels_tokens = self.events_sub(session_id)
            async for msg in ws:
                data = json.loads(msg.data)
                metadata = data["metadata"]
                if msg.type == web.WSMsgType.TEXT:
                    if (
                        metadata.get("subscription_type", None)
                        and metadata["subscription_type"] == "stream.online"
                    ):
                        logging.info("Stream live message received")
                        game_name, title = self.get_stream_info()
                        my_links = """
                        https://www.twitch.tv/pandagoria
                        https://live.vkplay.ru/pandagoria
                        """
                        await self.discord_bot.publish(
                            "announcement",
                            f"""{title}: {game_name.upper()}
                            {my_links}""",
                        )
                    elif metadata["message_type"] == "session_reconnect":
                        logging.info("Session reconnect message received.")
                        self.config.eventsub["websocket_url"] = data["payload"][
                            "reconnect_url"
                        ]
                        raise ClientError(
                            "I dunno which exception would fit but it's for reconnection"
                        )
                elif msg.type == web.WSMsgType.ERROR:
                    raise ServerDisconnectedError()

            logging.info("Disconnected")
            self.auth_session.close()


if __name__ == "__main__":
    twitch = TwitchClient()
    asyncio.run(twitch.websocket_session())
