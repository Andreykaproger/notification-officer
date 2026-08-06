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
    ):  # -> str | None
        self._verifier.verify(
            request.message_id,
            request.timestamp,
            request.request_body,
            request.signature,
        )

        payload = json.loads(request.request_body)

        match request.message_type:
            case EventSubMessageType.REVOCATION:
                return await self._handle_revocation()

            case EventSubMessageType.NOTIFICATION:
                event = payload["event"]
                return await self._handle_notification(
                    StreamOnlineNotification(
                        broadcaster_user_id=event["broadcaster_user_id"],
                        broadcaster_user_login=event["broadcaster_user_login"],
                        broadcaster_user_name=event["broadcaster_user_name"],
                        started_at=datetime.fromisoformat(
                            event["started_at"].replace("Z", "+00:00")
                        ),
                    )
                )

            case EventSubMessageType.WEBHOOK_CALLBACK_VERIFICATION:
                return await self._handle_callback_verification(payload["challenge"])

    async def _handle_revocation(
        self,
    ):
        return None

    async def _handle_notification(
        self,
        event: StreamOnlineNotification,
    ) -> StreamOnlineNotification:
        logger.info(event)
        return event

    async def _handle_callback_verification(self, challenge: str) -> str:
        return challenge
