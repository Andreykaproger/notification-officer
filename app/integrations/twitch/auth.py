import asyncio
import time

import httpx

from app.core.config import Settings
from app.integrations.twitch.dto import OAuthToken
from app.integrations.twitch.exceptions import TwitchApiError, TwitchAuthenticationError


class TwitchAuthClient:
    _TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    _REFRESH_MARGIN = 60

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        settings: Settings,
    ) -> None:
        self._token: OAuthToken | None = None
        self._expires_at: float | None = None
        self._lock = asyncio.Lock()
        self._http_client = http_client
        self._settings = settings

    def _has_valid_token(self) -> bool:
        return (
            self._token is not None
            and self._expires_at is not None
            and time.monotonic() < self._expires_at
        )

    async def get_app_access_token(self) -> OAuthToken:
        if self._has_valid_token():
            assert self._token is not None
            return self._token

        async with self._lock:
            if self._has_valid_token():
                assert self._token is not None
                return self._token

            try:
                response = await self._http_client.post(
                    self._TOKEN_URL,
                    params={
                        "client_id": self._settings.twitch_client_id,
                        "client_secret": self._settings.twitch_client_secret,
                        "grant_type": "client_credentials",
                    },
                )

                response.raise_for_status()

            except httpx.HTTPStatusError as exc:
                raise TwitchAuthenticationError() from exc
            except httpx.RequestError as exc:
                raise TwitchApiError("Request token Twitch API error") from exc

            payload = response.json()
            oauth_token = OAuthToken(**payload)

            self._token = oauth_token
            self._expires_at = (
                time.monotonic() + oauth_token.expires_in - self._REFRESH_MARGIN
            )

            return oauth_token
