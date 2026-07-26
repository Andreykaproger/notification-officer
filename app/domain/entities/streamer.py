from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Streamer:
    id: int | None
    twitch_id: str
    login: str
    display_name: str
    created_at: datetime | None = None
