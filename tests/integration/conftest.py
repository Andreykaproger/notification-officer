import json
from datetime import datetime
from unittest.mock import Mock

import pytest
from redis.asyncio import Redis

from app.application.handlers.registry import HandlerRegistry
from app.application.handlers.twitch import TwitchHandler
from app.application.publishers.notification_publisher import NotificationPublisher
from app.application.services.eventsub_service import EventSubWebhookService
from app.application.workers.notification_worker import NotificationWorker
from app.infrastructure.redis.connector import RedisConnector
from app.infrastructure.redis.stream_consumer import RedisStreamConsumer
from app.infrastructure.redis.stream_initializer import RedisStreamInitializer
from app.integrations.twitch.dto import EventSubMessageType, EventSubWebhookRequest


@pytest.fixture
async def clean_redis(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6380")

    redis = Redis(
        host="localhost",
        port=6380,
        decode_responses=True,
    )

    try:
        await redis.flushdb()
        yield
    finally:
        await redis.flushdb()
        await redis.aclose()


@pytest.fixture
async def redis_client():

    redis_client = Redis(
        host="localhost",
        port=6380,
        decode_responses=True,
    )
    try:
        await redis_client.flushdb()

        yield redis_client
    finally:
        await redis_client.flushdb()
        await redis_client.aclose()


@pytest.fixture
def twitch_handler():
    return TwitchHandler()


@pytest.fixture
def handler_registry(twitch_handler):
    return HandlerRegistry({"twitch": twitch_handler})


@pytest.fixture
async def redis_connector(
    redis_client,
):
    return RedisConnector(redis_client)


@pytest.fixture
async def publisher(
    redis_connector,
):
    return NotificationPublisher(redis_connector)


@pytest.fixture
async def eventsub_service(
    publisher,
):
    verifier = Mock()
    return EventSubWebhookService(
        publisher=publisher,
        verifier=verifier,
    )


@pytest.fixture
async def consumer(
    redis_client,
):
    initializer = RedisStreamInitializer(redis_client)
    await initializer.create_consumer_group()

    return RedisStreamConsumer(redis_client)


@pytest.fixture
async def notification_worker(
    consumer,
    handler_registry,
):
    return NotificationWorker(
        consumer=consumer,
        handler_registry=handler_registry,
    )


@pytest.fixture
def webhook_request_stream_online():
    payload = {
        "subscription": {"type": "stream.online"},
        "event": {
            "broadcaster_user_id": "1",
            "broadcaster_user_login": "test",
            "broadcaster_user_name": "test",
            "started_at": "2026-07-22T12:00:00+00:00",
        },
    }

    request_body = json.dumps(payload).encode("utf-8")
    return EventSubWebhookRequest(
        request_body=request_body,
        message_type=EventSubMessageType.NOTIFICATION,
        message_id="1",
        timestamp=datetime(2026, 7, 22, 12, 0, 0).isoformat(),
        signature="signature",
    )


@pytest.fixture
def webhook_request_stream_offline():
    payload = {
        "subscription": {"type": "stream.offline"},
        "event": {
            "broadcaster_user_id": "1",
            "broadcaster_user_login": "test",
            "broadcaster_user_name": "test",
        },
    }

    request_body = json.dumps(payload).encode("utf-8")
    return EventSubWebhookRequest(
        request_body=request_body,
        message_type=EventSubMessageType.NOTIFICATION,
        message_id="1",
        timestamp=datetime(2026, 7, 22, 12, 0, 0).isoformat(),
        signature="signature",
    )


@pytest.fixture
def webhook_request_channel_update():
    payload = {
        "subscription": {"type": "channel.update"},
        "event": {
            "broadcaster_user_id": "1",
            "broadcaster_user_login": "test",
            "broadcaster_user_name": "test",
            "title": "stream",
            "category_name": "stream",
        },
    }

    request_body = json.dumps(payload).encode("utf-8")
    return EventSubWebhookRequest(
        request_body=request_body,
        message_type=EventSubMessageType.NOTIFICATION,
        message_id="1",
        timestamp=datetime(2026, 7, 22, 12, 0, 0).isoformat(),
        signature="signature",
    )
