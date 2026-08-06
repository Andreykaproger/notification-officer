import logging
from datetime import datetime

import httpx

from app.core.config import Settings
from app.integrations.twitch.auth import TwitchAuthClient
from app.integrations.twitch.dto import EventSubscription, StreamOnlineCondition
from app.integrations.twitch.enums import EventSubStatus, EventSubType
from app.integrations.twitch.exceptions import EventSubClientError

logger = logging.getLogger()


class EventSubClient:
    _BASE_URL = "https://api.twitch.tv/helix"
    _SUBSCRIPTIONS_ENDPOINT = "/eventsub/subscriptions"
    _EVENT_VERSIONS = {
        EventSubType.STREAM_ONLINE: "1",
        EventSubType.STREAM_OFFLINE: "1",
        EventSubType.CHANNEL_UPDATE: "2",
    }

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_client: TwitchAuthClient,
        settings: Settings,
    ) -> None:
        self._http_client = http_client
        self._auth_client = auth_client
        self._secret = settings.twitch_webhook_secret
        self._client_id = settings.twitch_client_id
        self._callback_url = settings.twitch_callback_url

    async def create_subscription(
        self, event_type: EventSubType, condition: StreamOnlineCondition
    ) -> EventSubscription:

        token = await self._auth_client.get_app_access_token()

        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Client-Id": self._client_id,
        }

        payload = {
            "type": event_type.value,
            "version": self._EVENT_VERSIONS[event_type],
            "condition": {
                "broadcaster_user_id": condition.broadcaster_user_id,
            },
            "transport": {
                "method": "webhook",
                "callback": self._callback_url,
                "secret": self._secret,
            },
        }

        try:
            response = await self._http_client.post(
                f"{self._BASE_URL}{self._SUBSCRIPTIONS_ENDPOINT}",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            logger.exception("EventSub API Error Later Add Retry worker")
            raise EventSubClientError(
                f"EventSub API returned {err.response.status_code}, {err.response.text}"
            ) from err
        except httpx.RequestError as err:
            raise EventSubClientError("Request EventSub API error") from err

        data = response.json()["data"][0]

        return EventSubscription(
            id=data["id"],
            status=EventSubStatus(data["status"]),
            type=EventSubType(data["type"]),
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
        )
