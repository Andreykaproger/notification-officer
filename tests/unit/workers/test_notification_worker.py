from unittest.mock import AsyncMock, Mock

from app.application.exceptions.base import TemporaryNotificationError
from app.application.exceptions.handler import NotificationHandlerNotFound
from app.application.workers.notification_worker import NotificationWorker
from app.infrastructure.redis.dto import RedisStreamMessage
from app.integrations.dto import NotificationMessage


async def test_process_message_correct():
    consumer = AsyncMock()
    registry = Mock()
    handler = Mock()
    registry.get.return_value = handler
    consumer.consume.return_value = RedisStreamMessage(
        message_id="1234",
        payload="""
        {"platform": "twitch", 
        "event_type": "stream.online", 
        "payload": {"payload": "payload"}}""".strip(),
    )

    worker = NotificationWorker(consumer, registry)

    await worker.process_message()

    consumer.consume.assert_awaited_once()
    registry.get.assert_called_once_with("twitch")
    consumer.ack.assert_awaited_once_with("1234")
    handler.handle.assert_called_once_with(
        NotificationMessage(
            platform="twitch",
            event_type="stream.online",
            payload={"payload": "payload"},
        )
    )


async def test_process_message_permanent_error():
    consumer = AsyncMock()
    registry = Mock()
    registry.get.side_effect = NotificationHandlerNotFound()
    consumer.consume.return_value = RedisStreamMessage(
        message_id="1234",
        payload="""
        {"platform": "invalid_platform", 
        "event_type": "stream.online", 
        "payload": {"payload": "payload"}}""".strip(),
    )

    worker = NotificationWorker(consumer, registry)

    await worker.process_message()

    consumer.consume.assert_awaited_once()
    consumer.ack.assert_awaited_once_with("1234")
    registry.get.assert_called_once_with("invalid_platform")


async def test_process_message_temporary_error():
    consumer = AsyncMock()
    registry = Mock()
    handler = Mock()
    registry.get.return_value = handler
    handler.handle.side_effect = TemporaryNotificationError()

    consumer.consume.return_value = RedisStreamMessage(
        message_id="1234",
        payload="""
        {"platform": "temporary_platform", 
        "event_type": "stream.online", 
        "payload": {"payload": "payload"}}""".strip(),
    )

    worker = NotificationWorker(consumer, registry)

    await worker.process_message()

    consumer.consume.assert_awaited_once()
    consumer.ack.assert_not_awaited()
    registry.get.assert_called_once_with("temporary_platform")
    handler.handle.assert_called_once_with(
        NotificationMessage(
            platform="temporary_platform",
            event_type="stream.online",
            payload={"payload": "payload"},
        )
    )
