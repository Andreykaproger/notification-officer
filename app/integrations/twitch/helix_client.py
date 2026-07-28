from datetime import datetime
from typing import Any

import httpx

from app.core.config import Settings
from app.integrations.twitch.auth import TwitchAuthClient
from app.integrations.twitch.dto import HelixStream, HelixUser
from app.integrations.twitch.exceptions import (
    TwitchApiError,
    TwitchUserNotFoundError,
)


class HelixClient:
    _BASE_URL = "https://api.twitch.tv/helix"
    _USERS_ENDPOINT = "/users"
    _STREAMS_ENDPOINT = "/streams"

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_client: TwitchAuthClient,
        settings: Settings,
    ) -> None:
        self._http_client = http_client
        self._auth_client = auth_client
        self._settings = settings

    async def _request(
        self,
        endpoint: str,
        params: Any,
    ) -> httpx.Response:

        token = await self._auth_client.get_app_access_token()
        try:
            response = await self._http_client.get(
                url=f"{self._BASE_URL}{endpoint}",
                params=params,
                headers={
                    "Authorization": f"Bearer {token.access_token}",
                    "Client-Id": self._settings.twitch_client_id,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            raise TwitchApiError(
                f"Twitch API returned {err.response.status_code}"
            ) from err
        except httpx.RequestError as err:
            raise TwitchApiError("Request Twitch API error") from err

        return response

    async def get_user_by_login(self, login: str) -> HelixUser:

        response = await self._request(
            endpoint=self._USERS_ENDPOINT,
            params={
                "login": login,
            },
        )

        users = response.json()["data"]

        if not users:
            raise TwitchUserNotFoundError(login)

        user = users[0]

        return HelixUser(
            id=user["id"],
            login=user["login"],
            display_name=user["display_name"],
        )

    async def get_users(self, logins: list[str]) -> list[HelixUser]:

        response = await self._request(
            endpoint=self._USERS_ENDPOINT,
            params=[("login", login) for login in logins],
        )

        users = response.json()["data"]

        if not users:
            return []

        return [
            HelixUser(
                id=user["id"], login=user["login"], display_name=user["display_name"]
            )
            for user in users
        ]

    async def get_stream_by_user_id(self, user_id: str) -> HelixStream | None:

        response = await self._request(
            endpoint=self._STREAMS_ENDPOINT,
            params={
                "user_id": user_id,
            },
        )

        streams = response.json()["data"]

        if not streams:
            return None

        stream = streams[0]

        return HelixStream(
            id=stream["id"],
            user_id=stream["user_id"],
            game_id=stream["game_id"],
            game_name=stream["game_name"],
            title=stream["title"],
            started_at=datetime.fromisoformat(
                stream["started_at"].replace("Z", "+00:00")
            ),
        )
