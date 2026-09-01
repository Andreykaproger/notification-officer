from unittest.mock import AsyncMock

import pytest
from redis.exceptions import RedisError

from app.infrastructure.redis.connector import RedisConnector
from app.infrastructure.redis.exceptions import RedisConnectorError


async def test_xadd_correct():
    redis_client = AsyncMock()

    redis_client.xadd.return_value = "123-0"

    redis_connector = RedisConnector(redis_client)
    message = {"message": "test_message"}

    result = await redis_connector.xadd("test", message)

    redis_client.xadd.assert_awaited_once_with("test", message)

    assert result == "123-0"


async def test_xadd_redis_error():
    redis_client = AsyncMock()
    redis_client.xadd.side_effect = RedisError()

    redis_connector = RedisConnector(redis_client)

    with pytest.raises(RedisConnectorError) as exc_info:
        await redis_connector.xadd("test", {"message": "test_message"})

    redis_client.xadd.assert_awaited_once_with("test", {"message": "test_message"})

    assert str(exc_info.value) == "Failed to execute Redis command"
    assert isinstance(exc_info.value.__cause__, RedisError)
