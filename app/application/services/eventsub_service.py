import json
from logging import getLogger

from app.application.publishers.notification_publisher import NotificationPublisher
from app.integrations.dto import NotificationMessage
from app.integrations.twitch.dto import EventSubWebhookRequest
from app.integrations.twitch.enums import EventSubMessageType
from app.integrations.twitch.verifier import TwitchSignatureVerifier

logger = getLogger(__name__)


class EventSubWebhookService:
    def __init__(
        self, verifier: TwitchSignatureVerifier, publisher: NotificationPublisher
    ) -> None:
        self._verifier = verifier
        self._publisher = publisher

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
                event_type = payload["subscription"]["type"]
                await self._handle_notification(event=event, event_type=event_type)
                return None

            case EventSubMessageType.WEBHOOK_CALLBACK_VERIFICATION:
                return await self._handle_callback_verification(payload["challenge"])

    async def _handle_revocation(
        self,
    ) -> None:
        logger.info("Twitch EventSub subscription revoked")

    async def _handle_notification(self, event: dict, event_type: str) -> None:

        notification_message = NotificationMessage(
            platform="twitch", event_type=event_type, payload=event
        )

        await self._publisher.publish(notification_message)

    async def _handle_callback_verification(self, challenge: str) -> str:
        logger.info("Twitch EventSub callback verification received")
        return challenge
