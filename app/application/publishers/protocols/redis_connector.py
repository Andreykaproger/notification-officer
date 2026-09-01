from typing import Protocol


class RedisConnectorProtocol(Protocol):
    async def xadd(
        self,
        stream_name: str,
        message: dict[str, str],
    ) -> str:
        """Add a new message to Redis Streams"""
        pass
