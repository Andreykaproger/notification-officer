from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class NotificationMessage:
    platform: str
    event_type: str
    payload: dict[str, Any]
