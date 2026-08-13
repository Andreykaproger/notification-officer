import json
from datetime import datetime
from logging import getLogger

from app.integrations.twitch.dto import EventSubWebhookRequest, StreamOnlineNotification
from app.integrations.twitch.enums import EventSubMessageType
from app.integrations.twitch.verifier import TwitchSignatureVerifier

logger = getLogger(__name__)


class EventSubWebhookService:
    def __init__(
        self,
        verifier: TwitchSignatureVerifier,
    ) -> None:
        self._verifier = verifier

    async def handle(
        self,
        request: EventSubWebhookRequest,
    ) -> str | None:
        self._verifier.verify(
            request.message_id,
            request.timestamp,
            request.request_body,
            request.signature,
        )

        payload = json.loads(request.request_body)

        match request.message_type:
            case EventSubMessageType.REVOCATION:
                await self._handle_revocation()
                return None

            case EventSubMessageType.NOTIFICATION:
                event = payload["event"]
                await self._handle_notification(
                    StreamOnlineNotification(
                        broadcaster_user_id=event["broadcaster_user_id"],
                        broadcaster_user_login=event["broadcaster_user_login"],
                        broadcaster_user_name=event["broadcaster_user_name"],
                        started_at=datetime.fromisoformat(
                            event["started_at"].replace("Z", "+00:00")
                        ),
                    )
                )
                return None

            case EventSubMessageType.WEBHOOK_CALLBACK_VERIFICATION:
                return await self._handle_callback_verification(payload["challenge"])

    async def _handle_revocation(
        self,
    ) -> None:
        logger.info("Twitch EventSub subscription revoked")

    async def _handle_notification(
        self,
        event: StreamOnlineNotification,
    ) -> None:
        logger.info(
            "Twitch stream online: broadcaster=%s login=%s",
            event.broadcaster_user_id,
            event.broadcaster_user_login,
        )

    async def _handle_callback_verification(self, challenge: str) -> str:
        logger.info("Twitch EventSub callback verification received")
        return challenge
