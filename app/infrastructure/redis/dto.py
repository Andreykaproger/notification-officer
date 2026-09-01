from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RedisStreamMessage:
    message_id: str
    payload: str
