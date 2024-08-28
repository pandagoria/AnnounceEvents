import logging
from requests_oauthlib import OAuth2Session
import json
from aiohttp import ClientSession, web, WSServerHandshakeError, WSMsgType
from aiohttp import web
import asyncio

from entities import Config


class TwitchClient:
    def __init__(self, discord_bot=None) -> None:
        self.config = Config("config/twitch_config.json")
        self.auth_session = None
        self.discord_bot = discord_bot
        self.loop = asyncio.get_event_loop()
        self.on_startup()

    def on_startup(self) -> None:
        self.authorize()
        self.get_panda_user_id()
        self.loop.create_task(self.websocket_session())

    def authorize(self) -> None:
        self.auth_session = OAuth2Session(
            self.config.client_id,
            redirect_uri=self.config.redirect_uri,
            scope=self.config.scope,
            token=self.config.token,
        )
        # authorization_url, _ = self.auth_session.authorization_url(
        #     self.config.oauth_url + "/authorize"
        # )
        # print(f"Please go to {authorization_url} and authorize access.")
        # authorization_response = input("Enter the full callback URL")
        # try:
        #     self.config.token = self.auth_session.fetch_token(
        #         self.config.oauth_url + "/token",
        #         verify=False,
        #         authorization_response=authorization_response,
        #         client_secret=self.config.client_secret,
        #         include_client_id=self.config.client_id,
        #         access_type="authorization_code",
        #         method="POST",
        #     )
        #     logging.info(self.config.token)

        # except Exception as e:
        #     logging.fatal(e)
        #     # self.auth_session.refresh_token(self.oauth_url + "/token",
        #     #                            refresh_token=self.config["token"]["refresh_token"])
        if not self.config.token:
            # Процесс первой авторизации
            authorization_url, _ = self.auth_session.authorization_url(
                self.config.oauth_url + "/authorize"
            )
            print(f"Please go to {authorization_url} and authorize access.")
            authorization_response = input("Enter the full callback URL: ")
            self.config.token = self.auth_session.fetch_token(
                self.config.oauth_url + "/token",
                authorization_response=authorization_response,
                client_secret=self.config.client_secret,
            )
        else:
            # Обновление токена с использованием рефреш токена
            extra = {
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
            self.config.token = self.auth_session.refresh_token(
                self.config.oauth_url + "/token",
                refresh_token=self.config.token["refresh_token"],
                **extra,
            )
        logging.info(self.config.token)

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

    def events_sub(self, session_id):
        data = {
            "type": self.config.eventsub["eventsubs"],
            "version": "1",
            "condition": {"broadcaster_user_id": self.config.user_id},
            "transport": {"method": "websocket", "session_id": session_id},
        }
        if self.auth_session is None:
            self.auth_session = OAuth2Session(
                self.config.client_id,
                redirect_uri=self.config.redirect_uri,
                scope=self.config.scope,
                token=self.config.token,
            )
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
            while True:
                try:
                    await self.run_ws(session)
                except WSServerHandshakeError:
                    logging.error("WebSocket handshake error. Retrying...")
                    await asyncio.sleep(5)
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    await asyncio.sleep(5)

    async def run_ws(self, session) -> None:
        async with session.ws_connect(self.config.eventsub["websocket_url"]) as ws:
            res = await ws.receive()
            session_id = json.loads(res.data)["payload"]["session"]["id"]
            logging.info("Connected")
            private_channels_tokens = self.events_sub(session_id)
            logging.info(private_channels_tokens)
            async for msg in ws:
                logging.info(msg.data)
                metadata = json.loads(msg.data)["metadata"]
                if msg.type == web.WSMsgType.TEXT:
                    if (
                        metadata.get("subscription_type", None) is not None
                        and metadata["subscription_type"] == "stream.online"
                    ):
                        await self.discord_bot.publish(
                            "announcement",
                            "Ку! Стрим начался!\n https://www.twitch.tv/pandagoria https://live.vkplay.ru/pandagoria",
                        )
                    elif metadata["message_type"] == "session_reconnect":
                        logging.info("Session reconnect message received.")
                        self.config.eventsub["websocket_url"] = json.loads(msg.data)[
                            "payload"
                        ]["retry_connection_url"]
                        raise WSServerHandshakeError()
                elif msg.type == web.WSMsgType.ERROR:
                    raise WSServerHandshakeError()

            logging.info("Disconnected")

    def __del__(self):
        self.auth_session.close()


if __name__ == "__main__":
    pass
