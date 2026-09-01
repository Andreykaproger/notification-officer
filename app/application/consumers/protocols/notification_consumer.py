from typing import Protocol

from app.infrastructure.redis.dto import RedisStreamMessage


class RedisStreamConsumerProtocol(Protocol):
    async def consume(self) -> RedisStreamMessage:
        """Get messages from Redis stream"""
        pass

    async def ack(self, message_id: str) -> None:
        """confirmation of processing Redis message"""
        pass

    async def reclaim_pending(
        self,
        min_idle_time_ms: int,
        count: int,
    ) -> list[RedisStreamMessage]:
        """Reclaim pending messages over min_idle_time"""
        pass
