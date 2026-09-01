import json
from unittest.mock import AsyncMock

import pytest

from app.infrastructure.redis.exceptions import RedisConnectorError
from app.integrations.dto import NotificationMessage
from app.integrations.twitch.exceptions import InvalidTwitchSignatureError


async def test_handle_invalid_signature(
    eventsub_service,
    verifier,
    webhook_request_verification,
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
    notification_publisher,
    verifier,
    webhook_request_notification,
):
    verifier.verify.return_value = None

    result = await eventsub_service.handle(webhook_request_notification)

    verifier.verify.assert_called_once_with(
        webhook_request_notification.message_id,
        webhook_request_notification.timestamp,
        webhook_request_notification.request_body,
        webhook_request_notification.signature,
    )

    payload = json.loads(webhook_request_notification.request_body)

    expected = NotificationMessage(
        platform="twitch",
        event_type=payload["subscription"]["type"],
        payload=payload["event"],
    )

    notification_publisher.publish.assert_awaited_once_with(expected)

    assert result is None


async def test_handle_notification_redis_error(
    eventsub_service,
    notification_publisher,
    verifier,
    webhook_request_notification,
):
    verifier.verify.return_value = None
    notification_publisher.publish.side_effect = RedisConnectorError()

    with pytest.raises(RedisConnectorError):
        await eventsub_service.handle(webhook_request_notification)

    payload = json.loads(webhook_request_notification.request_body)

    verifier.verify.assert_called_once_with(
        webhook_request_notification.message_id,
        webhook_request_notification.timestamp,
        webhook_request_notification.request_body,
        webhook_request_notification.signature,
    )

    expected = NotificationMessage(
        platform="twitch",
        event_type=payload["subscription"]["type"],
        payload=payload["event"],
    )

    notification_publisher.publish.assert_awaited_once_with(expected)


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
