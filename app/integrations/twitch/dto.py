from dataclasses import dataclass
from datetime import datetime


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
