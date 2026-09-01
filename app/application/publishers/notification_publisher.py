from app.application.publishers.protocols.redis_connector import RedisConnectorProtocol
from app.integrations.dto import NotificationMessage
from app.integrations.serializers import NotificationMessageSerializer


class NotificationPublisher:
    _STREAM_NAME = "notifications"

    def __init__(self, redis_connector: RedisConnectorProtocol) -> None:
        self._redis_connector = redis_connector

    async def publish(self, notification: NotificationMessage) -> str:

        json_message = NotificationMessageSerializer.to_json(notification)
        redis_message = {"message": json_message}

        notification_id = await self._redis_connector.xadd(
            self._STREAM_NAME, redis_message
        )

        return notification_id
