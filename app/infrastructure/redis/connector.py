from typing import cast

from redis.asyncio import Redis
from redis.exceptions import RedisError
from redis.typing import EncodableT, FieldT

from app.infrastructure.redis.exceptions import RedisConnectorError


class RedisConnector:
    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client

    async def xadd(
        self,
        stream_name: str,
        message: dict[str, str],
    ) -> str:

        redis_message = cast(dict[FieldT, EncodableT], message)
        try:
            result_id = await self._redis_client.xadd(
                stream_name,
                redis_message,
            )
        except RedisError as exc:
            raise RedisConnectorError() from exc

        assert isinstance(result_id, str)

        return result_id
