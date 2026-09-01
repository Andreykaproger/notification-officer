from unittest.mock import AsyncMock

import pytest

from app.application.publishers.notification_publisher import NotificationPublisher
from app.infrastructure.redis.exceptions import RedisConnectorError
from app.integrations.exceptions import NotificationSerializationError
from app.integrations.serializers import NotificationMessageSerializer


async def test_publish_correct(
    notification_message,
):
    redis_connector = AsyncMock()
    redis_connector.xadd.return_value = "1234"

    publisher = NotificationPublisher(redis_connector)

    result = await publisher.publish(notification_message)

    json_message = NotificationMessageSerializer.to_json(notification_message)
    message = {"message": json_message}

    redis_connector.xadd.assert_awaited_once_with("notifications", message)
    assert result == "1234"


async def test_publish_serializer_error(
    invalid_notification_message,
):
    redis_connector = AsyncMock()

    publisher = NotificationPublisher(redis_connector)

    with pytest.raises(NotificationSerializationError):
        await publisher.publish(invalid_notification_message)

    redis_connector.xadd.assert_not_awaited()


async def test_publish_redis_connection_error(
    notification_message,
):
    redis_connector = AsyncMock()
    redis_connector.xadd.side_effect = RedisConnectorError()
    publisher = NotificationPublisher(redis_connector)

    with pytest.raises(RedisConnectorError):
        await publisher.publish(notification_message)

    redis_connector.xadd.assert_awaited_once()
