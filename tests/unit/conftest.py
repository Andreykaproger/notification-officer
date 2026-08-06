import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.services.eventsub_service import EventSubWebhookService
from app.application.services.streamer_service import StreamerService
from app.domain.entities.streamer import Streamer
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
        "event": {
            "broadcaster_user_id": "1",
            "broadcaster_user_login": "test",
            "broadcaster_user_name": "test",
            "started_at": "2026-07-22T12:00:00+00:00",
        }
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
def eventsub_service(
    verifier,
):
    return EventSubWebhookService(
        verifier=verifier,
    )
