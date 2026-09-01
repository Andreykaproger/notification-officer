from unittest.mock import AsyncMock

import pytest
from redis import RedisError

from app.infrastructure.redis.dto import RedisStreamMessage
from app.infrastructure.redis.exceptions import (
    RedisConnectorError,
    RedisMessageFormatError,
)
from app.infrastructure.redis.stream_consumer import RedisStreamConsumer


async def test_consume_correct(redis_message, redis_stream_message):
    redis_client = AsyncMock()
    redis_client.xreadgroup.return_value = redis_message

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.consume()

    assert result == redis_stream_message

    redis_client.xreadgroup.assert_awaited_once()


async def test_consume_incorrect():
    redis_client = AsyncMock()
    redis_client.xreadgroup.side_effect = RedisError()

    consumer = RedisStreamConsumer(redis_client)

    with pytest.raises(RedisConnectorError) as exc_info:
        await consumer.consume()

    assert isinstance(exc_info.value.__cause__, RedisError)


async def test_consume_incorrect_missing_message_field(
    redis_message, redis_stream_message
):
    redis_client = AsyncMock()
    redis_client.xreadgroup.side_effect = [
        [
            ("notifications", [("1234-1", {"not_message": "{'payload': 'payload'}"})]),
        ],
        redis_message,
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.consume()

    assert result == redis_stream_message
    assert redis_client.xreadgroup.await_count == 2
    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", "1234-1"
    )


async def test_consume_invalid_message_type(redis_message, redis_stream_message):
    redis_client = AsyncMock()
    redis_client.xreadgroup.side_effect = [
        [
            ("notifications", [("1234-1", {"message": b"not_str"})]),
        ],
        redis_message,
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.consume()

    assert result == redis_stream_message
    assert redis_client.xreadgroup.await_count == 2

    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", "1234-1"
    )


async def test_consume_retries_when_result_is_empty(
    redis_message, redis_stream_message
):
    redis_client = AsyncMock()
    redis_client.xreadgroup.side_effect = [[], redis_message]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.consume()

    assert result == redis_stream_message
    assert redis_client.xreadgroup.await_count == 2


async def test_ack_correct():
    redis_client = AsyncMock()
    message_id = "1234"

    consumer = RedisStreamConsumer(redis_client)
    await consumer.ack(message_id)

    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", message_id
    )


async def test_ack_incorrect():
    redis_client = AsyncMock()
    redis_client.xack.side_effect = RedisError()
    consumer = RedisStreamConsumer(redis_client)

    with pytest.raises(RedisConnectorError):
        await consumer.ack("1234")

    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", "1234"
    )


async def test_reclaim_pending_get_two_pending_return_two_rsm():
    redis_client = AsyncMock()
    redis_client.xautoclaim.return_value = [
        "next_start_id",
        [
            ("1234-0", {"message": "{'payload': 'payload'}"}),
            ("1234-1", {"message": "{'payload': 'sec_payload'}"}),
        ],
        "deleted_ids",
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.reclaim_pending(min_idle_time_ms=3000, count=10)

    expected = [
        RedisStreamMessage(
            message_id="1234-0",
            payload="{'payload': 'payload'}",
        ),
        RedisStreamMessage(
            message_id="1234-1",
            payload="{'payload': 'sec_payload'}",
        ),
    ]

    assert result == expected
    redis_client.xautoclaim.assert_awaited_once_with(
        "notifications",
        "notification-workers",
        consumer._consumer_name,
        min_idle_time=3000,
        count=10,
        start_id="0-0",
    )


async def test_reclaim_pending_get_two_pending_return_one_rsm():
    redis_client = AsyncMock()
    redis_client.xautoclaim.return_value = [
        "next_start_id",
        [
            ("1234-0", {"message": "{'payload': 'payload'}"}),
            ("1234-1", {"not_message": "{'payload': 'bad_payload'}"}),
            ("1234-2", {"message": "{'payload': 'sec_payload'}"}),
        ],
        "deleted_ids",
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.reclaim_pending(min_idle_time_ms=3000, count=10)

    expected = [
        RedisStreamMessage(
            message_id="1234-0",
            payload="{'payload': 'payload'}",
        ),
        RedisStreamMessage(
            message_id="1234-2",
            payload="{'payload': 'sec_payload'}",
        ),
    ]

    assert result == expected
    redis_client.xautoclaim.assert_awaited_once()
    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", "1234-1"
    )


async def test_reclaim_pending_no_pending_messages():
    redis_client = AsyncMock()
    redis_client.xautoclaim.return_value = [
        "0-0",
        [],
        [],
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.reclaim_pending(30, 10)

    assert result == []

    redis_client.xautoclaim.assert_awaited_once_with(
        "notifications",
        "notification-workers",
        consumer._consumer_name,
        min_idle_time=30,
        count=10,
        start_id="0-0",
    )


async def test_reclaim_pending_incorrect():
    redis_client = AsyncMock()
    redis_client.xautoclaim.side_effect = RedisError()

    consumer = RedisStreamConsumer(redis_client)
    with pytest.raises(RedisConnectorError) as exc_info:
        await consumer.reclaim_pending(30, 10)

    assert isinstance(exc_info.value.__cause__, RedisError)


async def test_reclaim_pending_missing_message_field():
    redis_client = AsyncMock()
    redis_client.xautoclaim.return_value = [
        "next_start_id",
        [
            ("1234-0", {"not_message": "{'payload': 'payload'}"}),
        ],
        "deleted_ids",
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.reclaim_pending(30, 10)

    assert result == []
    redis_client.xautoclaim.assert_awaited_once()
    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", "1234-0"
    )


async def test_reclaim_pending_invalid_message_type():
    redis_client = AsyncMock()
    redis_client.xautoclaim.return_value = [
        "next_start_id",
        [
            ("1234-0", {"message": b"not_str"}),
        ],
        "deleted_ids",
    ]

    consumer = RedisStreamConsumer(redis_client)
    result = await consumer.reclaim_pending(30, 10)
    assert result == []
    redis_client.xautoclaim.assert_awaited_once()
    redis_client.xack.assert_awaited_once_with(
        "notifications", "notification-workers", "1234-0"
    )


async def test_create_message_correct():
    redis_client = AsyncMock()
    message_id = "1234"
    data = {"message": "data"}
    consumer = RedisStreamConsumer(redis_client)

    result = await consumer._create_message(message_id, data)

    assert result == RedisStreamMessage(
        message_id=message_id,
        payload="data",
    )


async def test_create_message_missing_message_field():
    redis_client = AsyncMock()
    message_id = "1234"
    data = {"not_message": "not_message"}
    consumer = RedisStreamConsumer(redis_client)

    with pytest.raises(RedisMessageFormatError):
        await consumer._create_message(message_id, data)

    redis_client.xack.assert_awaited_once_with(
        "notifications",
        "notification-workers",
        message_id,
    )


async def test_create_message_invalid_message_type():
    redis_client = AsyncMock()
    message_id = "1234"
    data = {"message": b"not_str"}
    consumer = RedisStreamConsumer(redis_client)

    with pytest.raises(RedisMessageFormatError):
        await consumer._create_message(message_id, data)  # type: ignore

    redis_client.xack.assert_awaited_once_with(
        "notifications",
        "notification-workers",
        message_id,
    )


async def test_create_message_redis_error():
    redis_client = AsyncMock()
    redis_client.xack.side_effect = RedisError()
    message_id = "1234"
    data = {"message": b"message"}

    consumer = RedisStreamConsumer(redis_client)
    with pytest.raises(RedisConnectorError) as exc_info:
        await consumer._create_message(message_id, data)  # type: ignore

    redis_client.xack.assert_awaited_once_with(
        "notifications",
        "notification-workers",
        message_id,
    )

    assert isinstance(exc_info.value.__cause__, RedisError)
