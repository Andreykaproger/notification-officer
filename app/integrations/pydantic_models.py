from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class NotificationMessageModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    platform: str
    event_type: str
    payload: dict[str, Any]


class StreamOnlineNotification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str
    started_at: datetime


class StreamOfflineNotification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str


class ChannelUpdateNotification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str
    title: str
    category_name: str
