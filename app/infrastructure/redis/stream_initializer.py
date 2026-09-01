from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.infrastructure.redis.exceptions import RedisConnectorError


class RedisStreamInitializer:
    _STREAM_NAME = "notifications"
    _GROUP_NAME = "notification-workers"

    def __init__(
        self,
        redis_client: Redis,
    ) -> None:
        self._redis_client = redis_client

    async def create_consumer_group(self) -> None:

        try:
            await self._redis_client.xgroup_create(
                self._STREAM_NAME, self._GROUP_NAME, mkstream=True, id="$"
            )
        except RedisError as exc:
            if "BUSYGROUP" in str(exc):
                return

            raise RedisConnectorError() from exc
