from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from app.dependencies.twitch import get_event_sub_service
from app.integrations.twitch.dto import EventSubWebhookRequest
from app.integrations.twitch.enums import EventSubMessageType
from app.main import app


async def test_twitch_webhook_verification():
    service = AsyncMock()
    service.handle.return_value = "challenge"

    app.dependency_overrides[get_event_sub_service] = lambda: service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/twitch/webhook",
                content=b'{"challenge": "challenge"}',
                headers={
                    "Twitch-Eventsub-Message-Type": "webhook_callback_verification",
                    "Twitch-Eventsub-Message-Id": "message_id",
                    "Twitch-Eventsub-Message-Signature": "sha256=test",
                    "Twitch-Eventsub-Message-Timestamp": "2026-08-13T12:00:00Z",
                },
            )

        service.handle.assert_awaited_once()
        request_dto = service.handle.await_args.args[0]
        assert isinstance(request_dto, EventSubWebhookRequest)
        assert request_dto.message_type == (
            EventSubMessageType.WEBHOOK_CALLBACK_VERIFICATION
        )
        assert response.status_code == 200
        assert response.text == "challenge"

    finally:
        app.dependency_overrides.clear()


async def test_twitch_webhook_notification():
    service = AsyncMock()
    service.handle.return_value = None

    app.dependency_overrides[get_event_sub_service] = lambda: service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/twitch/webhook",
                content=b'{"data": "test"}',
                headers={
                    "Twitch-Eventsub-Message-Type": "notification",
                    "Twitch-Eventsub-Message-Id": "message_id",
                    "Twitch-Eventsub-Message-Signature": "sha256=test",
                    "Twitch-Eventsub-Message-Timestamp": "2026-08-13T12:00:00Z",
                },
            )

        assert response.status_code == 204
        assert response.content == b""

        service.handle.assert_awaited_once()
        request_dto = service.handle.await_args.args[0]

        assert isinstance(request_dto, EventSubWebhookRequest)
        assert request_dto.message_type == (EventSubMessageType.NOTIFICATION)
        assert request_dto.request_body == b'{"data": "test"}'
        assert request_dto.message_id == "message_id"
        assert request_dto.timestamp == "2026-08-13T12:00:00Z"
        assert request_dto.signature == "sha256=test"

    finally:
        app.dependency_overrides.clear()


async def test_twitch_webhook_invalid_message_type():
    service = AsyncMock()
    app.dependency_overrides[get_event_sub_service] = lambda: service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/twitch/webhook",
                content=b"something_wrong",
                headers={
                    "Twitch-Eventsub-Message-Type": "wrong_message_type",
                    "Twitch-Eventsub-Message-Id": "message_id",
                    "Twitch-Eventsub-Message-Signature": "sha256=test",
                    "Twitch-Eventsub-Message-Timestamp": "2026-08-13T12:00:00Z",
                },
            )

        assert response.status_code == 422

        service.handle.assert_not_awaited()

    finally:
        app.dependency_overrides.clear()
