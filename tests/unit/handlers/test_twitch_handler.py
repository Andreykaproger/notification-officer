import logging

import pytest
from pydantic import ValidationError

from app.application.exceptions.base import PermanentNotificationError
from app.application.handlers.twitch import TwitchHandler
from app.integrations.dto import NotificationMessage
from app.integrations.twitch.enums import EventSubType


@pytest.mark.parametrize(
    "event_type,payload,expected_logs",
    [
        (
            EventSubType.STREAM_ONLINE,
            {
                "broadcaster_user_id": "1234",
                "broadcaster_user_login": "user",
                "broadcaster_user_name": "user",
                "started_at": "2023-06-29T17:20:33.860897266Z",
            },
            [
                "Platform: Twitch",
                "Event: Streamer Online",
                "Streamer: user",
                "Link: https://twitch.tv/user",
            ],
        ),
        (
            EventSubType.STREAM_OFFLINE,
            {
                "broadcaster_user_id": "1234",
                "broadcaster_user_login": "user",
                "broadcaster_user_name": "user",
            },
            ["Platform: Twitch", "Event: Streamer Offline", "Streamer: user"],
        ),
        (
            EventSubType.CHANNEL_UPDATE,
            {
                "broadcaster_user_id": "1234",
                "broadcaster_user_login": "user",
                "broadcaster_user_name": "user",
                "title": "stream",
                "category_name": "stream",
            },
            [
                "Platform: Twitch",
                "Event: Channel Update",
                "Streamer: user",
                "Title: stream",
                "Category Name: stream",
            ],
        ),
    ],
)
def test_twitch_handler(event_type, payload, twitch_handler, expected_logs, caplog):
    caplog.set_level(logging.INFO)
    notification = NotificationMessage(
        platform="twitch", event_type=event_type, payload=payload
    )

    twitch_handler.handle(notification)

    for log in expected_logs:
        assert log in caplog.text


def test_handle_stream_online_ignore_unknown_fields():
    notification = NotificationMessage(
        platform="twitch",
        event_type="stream.online",
        payload={
            "broadcaster_user_id": "1234",
            "broadcaster_user_login": "user",
            "broadcaster_user_name": "user",
            "started_at": "2023-06-29T17:20:33.860897266Z",
            "unknown_field": "value",
        },
    )

    handler = TwitchHandler()

    handler.handle(notification)


def test_handle_unknown_event_type():
    notification = NotificationMessage(
        platform="twitch",
        event_type="unknown.event",
        payload={
            "broadcaster_user_id": 1234,
            "broadcaster_user_login": "user",
            "broadcaster_user_name": "user",
            "title": "stream",
            "category_name": "stream",
        },
    )

    handler = TwitchHandler()
    with pytest.raises(PermanentNotificationError) as exc_info:
        handler.handle(notification)

    assert str(exc_info.value) == "Invalid notification event type"


@pytest.mark.parametrize(
    "event_type,payload,error_message",
    [
        (
            EventSubType.STREAM_ONLINE,
            {
                "broadcaster_user_id": 1234,
                "broadcaster_user_login": "user",
                "broadcaster_user_name": "user",
                "started_at": "2023-06-29T17:20:33.860897266Z",
            },
            "Invalid Twitch stream.online payload",
        ),
        (
            EventSubType.STREAM_OFFLINE,
            {
                "broadcaster_user_id": 1234,
                "broadcaster_user_login": "user",
                "broadcaster_user_name": "user",
            },
            "Invalid Twitch stream.offline payload",
        ),
        (
            EventSubType.CHANNEL_UPDATE,
            {
                "broadcaster_user_id": 1234,
                "broadcaster_user_login": "user",
                "broadcaster_user_name": "user",
                "title": "stream",
                "category_name": "stream",
            },
            "Invalid Twitch channel.update payload",
        ),
    ],
)
def test_handle_invalid_payload(event_type, payload, error_message):
    notification = NotificationMessage(
        platform="twitch",
        event_type=event_type,
        payload=payload,
    )

    handler = TwitchHandler()

    with pytest.raises(PermanentNotificationError) as exc_info:
        handler.handle(notification)

    assert str(exc_info.value) == error_message
    assert isinstance(exc_info.value.__cause__, ValidationError)
