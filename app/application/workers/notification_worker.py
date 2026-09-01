import logging

from app.application.consumers.protocols.notification_consumer import (
    RedisStreamConsumerProtocol,
)
from app.application.exceptions.base import (
    PermanentNotificationError,
    TemporaryNotificationError,
)
from app.application.handlers.registry import HandlerRegistry
from app.integrations.serializers import NotificationMessageSerializer

logger = logging.getLogger(__name__)


class NotificationWorker:
    def __init__(
        self,
        consumer: RedisStreamConsumerProtocol,
        handler_registry: HandlerRegistry,
    ):
        self._consumer = consumer
        self._handler_registry = handler_registry

    async def process_message(self) -> None:

        message = await self._consumer.consume()
        try:
            notification = NotificationMessageSerializer.from_json(message.payload)

            handler = self._handler_registry.get(notification.platform)

            handler.handle(notification)

            await self._consumer.ack(message.message_id)

        except PermanentNotificationError as exc:
            logger.exception(exc)
            await self._consumer.ack(message.message_id)
        except TemporaryNotificationError as exc:
            logger.exception(exc)

    async def reclaim_pending(self) -> None:
        await self._consumer.reclaim_pending(
            min_idle_time_ms=30000,
            count=10,
        )
