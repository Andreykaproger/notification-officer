import logging
from typing import TypeVar

from pydantic import ValidationError

from app.application.exceptions.base import PermanentNotificationError
from app.integrations.dto import NotificationMessage
from app.integrations.pydantic_models import (
    ChannelUpdateNotification,
    StreamOfflineNotification,
    StreamOnlineNotification,
)
from app.integrations.twitch.enums import EventSubType

logger = logging.getLogger(__name__)

T = TypeVar(
    "T", StreamOnlineNotification, StreamOfflineNotification, ChannelUpdateNotification
)


class TwitchHandler:
    def handle(
        self,
        notification: NotificationMessage,
    ) -> None:

        match notification.event_type:
            case EventSubType.STREAM_ONLINE:
                self._handle_stream_online(notification.payload)
            case EventSubType.STREAM_OFFLINE:
                self._handle_stream_offline(notification.payload)
            case EventSubType.CHANNEL_UPDATE:
                self._handle_channel_update(notification.payload)
            case _:
                raise PermanentNotificationError("Invalid notification event type")

    def _validate_payload(
        self, model_type: type[T], payload: dict, error_message: str
    ) -> T:
        try:
            message = model_type.model_validate(payload)
        except ValidationError as exc:
            raise PermanentNotificationError(error_message) from exc
        return message

    def _handle_stream_online(
        self,
        payload: dict,
    ) -> None:
        message = self._validate_payload(
            model_type=StreamOnlineNotification,
            payload=payload,
            error_message="Invalid Twitch stream.online payload",
        )

        logger.info(
            """
            Platform: Twitch
            Event: Streamer Online
            Streamer: %s
            Link: https://twitch.tv/%s
            Started At: %s
            """,
            message.broadcaster_user_login,
            message.broadcaster_user_login,
            message.started_at,
        )

    def _handle_stream_offline(
        self,
        payload: dict,
    ) -> None:
        message = self._validate_payload(
            model_type=StreamOfflineNotification,
            payload=payload,
            error_message="Invalid Twitch stream.offline payload",
        )

        logger.info(
            """
            Platform: Twitch
            Event: Streamer Offline
            Streamer: %s
            """,
            message.broadcaster_user_login,
        )

    def _handle_channel_update(
        self,
        payload: dict,
    ) -> None:
        message = self._validate_payload(
            model_type=ChannelUpdateNotification,
            payload=payload,
            error_message="Invalid Twitch channel.update payload",
        )

        logger.info(
            """
            Platform: Twitch
            Event: Channel Update
            Streamer: %s
            Title: %s
            Category Name: %s
            """,
            message.broadcaster_user_login,
            message.title,
            message.category_name,
        )
