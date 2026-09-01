import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.handlers.twitch import TwitchHandler
from app.application.services.eventsub_service import EventSubWebhookService
from app.application.services.streamer_service import StreamerService
from app.domain.entities.streamer import Streamer
from app.infrastructure.redis.dto import RedisStreamMessage
from app.integrations.dto import NotificationMessage
from app.integrations.twitch.dto import EventSubWebhookRequest, HelixUser
from app.integrations.twitch.enums import EventSubMessageType


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def uow():
    return AsyncMock()


@pytest.fixture
def helix_client():
    return AsyncMock()


@pytest.fixture
def eventsub_client():
    return AsyncMock()


@pytest.fixture
def service(
    repository,
    uow,
    helix_client,
    eventsub_client,
):
    return StreamerService(
        repository=repository,
        uow=uow,
        helix_client=helix_client,
        eventsub_client=eventsub_client,
    )


@pytest.fixture
def streamer():
    return Streamer(
        id=None,
        twitch_id=None,
        login="shroud",
        display_name="Shroud",
        created_at=None,
    )


@pytest.fixture
def created_streamer():
    return Streamer(
        id=1,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
        created_at=datetime(2026, 7, 22, 12, 0, 0),
    )


@pytest.fixture
def helix_user():
    return HelixUser(
        id="123456",
        login="shroud",
        display_name="Shroud",
    )


@pytest.fixture
def verifier():
    return Mock()


@pytest.fixture
def webhook_request_verification():
    return EventSubWebhookRequest(
        request_body=b'{"challenge": "challenge"}',
        message_type=EventSubMessageType.WEBHOOK_CALLBACK_VERIFICATION,
        message_id="1",
        timestamp=datetime(2026, 7, 22, 12, 0, 0).isoformat(),
        signature="signature",
    )


@pytest.fixture
def webhook_request_notification():
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
def webhook_request_revocation():
    return EventSubWebhookRequest(
        request_body=b'{"revocation": "revocation"}',
        message_type=EventSubMessageType.REVOCATION,
        message_id="1",
        timestamp=datetime(2026, 7, 22, 12, 0, 0).isoformat(),
        signature="signature",
    )


@pytest.fixture
def notification_publisher():
    return AsyncMock()


@pytest.fixture
def eventsub_service(verifier, notification_publisher):
    return EventSubWebhookService(verifier=verifier, publisher=notification_publisher)


@pytest.fixture
def notification_message():
    return NotificationMessage(
        platform="test",
        event_type="test",
        payload={
            "message": "test message",
        },
    )


@pytest.fixture
def invalid_notification_message():
    return NotificationMessage(platform="test", event_type="test", payload="test")


@pytest.fixture
def dict_notification_message():
    return {
        "platform": "test",
        "event_type": "test",
        "payload": {
            "message": "test message",
        },
    }


@pytest.fixture
def invalid_dict_notification_message():
    return {"platform": "test", "event_type": "test", "payload": ["invalid"]}


@pytest.fixture
def redis_message():
    return [("notifications", [("1234-0", {"message": "{'payload': 'payload'}"})])]


@pytest.fixture
def redis_stream_message():
    return RedisStreamMessage(message_id="1234-0", payload="{'payload': 'payload'}")


@pytest.fixture
def twitch_handler():
    return TwitchHandler()
