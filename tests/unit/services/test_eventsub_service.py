from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.integrations.twitch.dto import StreamOnlineNotification
from app.integrations.twitch.exceptions import InvalidTwitchSignatureError


async def test_handle_invalid_signature(
    eventsub_service, verifier, webhook_request_verification
):

    verifier.verify.side_effect = InvalidTwitchSignatureError()

    with pytest.raises(InvalidTwitchSignatureError) as exc_info:
        await eventsub_service.handle(webhook_request_verification)

    verifier.verify.assert_called_once_with(
        webhook_request_verification.message_id,
        webhook_request_verification.timestamp,
        webhook_request_verification.request_body,
        webhook_request_verification.signature,
    )

    assert str(exc_info.value) == "Invalid Twitch webhook signature"


async def test_handle_verification(
    verifier,
    eventsub_service,
    webhook_request_verification,
):

    verifier.verify.return_value = None

    result = await eventsub_service.handle(webhook_request_verification)

    verifier.verify.assert_called_once_with(
        webhook_request_verification.message_id,
        webhook_request_verification.timestamp,
        webhook_request_verification.request_body,
        webhook_request_verification.signature,
    )

    assert result == "challenge"


async def test_handle_notification(
    eventsub_service,
    verifier,
    webhook_request_notification,
):
    verifier.verify.return_value = None

    eventsub_service._handle_notification = AsyncMock()
    result = await eventsub_service.handle(webhook_request_notification)

    verifier.verify.assert_called_once_with(
        webhook_request_notification.message_id,
        webhook_request_notification.timestamp,
        webhook_request_notification.request_body,
        webhook_request_notification.signature,
    )

    eventsub_service._handle_notification.assert_awaited_once()
    assert result is None


async def test_handle_notification_get_streamer_online_dto(
    eventsub_service,
    verifier,
    webhook_request_notification,
):
    verifier.verify.return_value = None
    eventsub_service._handle_notification = AsyncMock()

    await eventsub_service.handle(webhook_request_notification)

    eventsub_service._handle_notification.assert_awaited_once()

    event = eventsub_service._handle_notification.await_args.args[0]

    assert isinstance(event, StreamOnlineNotification)
    assert event.broadcaster_user_id == "1"
    assert event.broadcaster_user_login == "test"
    assert event.broadcaster_user_name == "test"
    assert event.started_at == datetime(2026, 7, 22, 12, 0, 0, tzinfo=timezone.utc)


async def test_handle_revocation(
    eventsub_service, webhook_request_revocation, verifier
):
    verifier.verify.return_value = None

    eventsub_service._handle_revocation = AsyncMock()

    result = await eventsub_service.handle(webhook_request_revocation)

    verifier.verify.assert_called_once_with(
        webhook_request_revocation.message_id,
        webhook_request_revocation.timestamp,
        webhook_request_revocation.request_body,
        webhook_request_revocation.signature,
    )

    eventsub_service._handle_revocation.assert_awaited_once()

    assert result is None
