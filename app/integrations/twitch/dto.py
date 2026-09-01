from dataclasses import dataclass
from datetime import datetime

from app.integrations.twitch.enums import (
    EventSubMessageType,
    EventSubStatus,
    EventSubType,
)


@dataclass(frozen=True)
class OAuthToken:
    access_token: str
    expires_in: int
    token_type: str


@dataclass(frozen=True)
class HelixUser:
    id: str
    login: str
    display_name: str


@dataclass(frozen=True)
class HelixStream:
    id: str
    user_id: str
    game_id: str
    game_name: str
    title: str
    started_at: datetime


@dataclass(frozen=True, slots=True)
class EventSubscription:
    id: str
    status: EventSubStatus
    type: EventSubType
    created_at: datetime


@dataclass(frozen=True, slots=True)
class EventSubWebhookRequest:
    request_body: bytes
    message_type: EventSubMessageType
    message_id: str
    timestamp: str
    signature: str


@dataclass(frozen=True, slots=True)
class StreamOnlineCondition:
    broadcaster_user_id: str
