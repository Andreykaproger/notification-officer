from unittest.mock import AsyncMock

import pytest
from redis.exceptions import RedisError, ResponseError

from app.infrastructure.redis.exceptions import RedisConnectorError
from app.infrastructure.redis.stream_initializer import RedisStreamInitializer


async def test_xgroup_create_correct():

    redis_client = AsyncMock()
    redis_client.xgroup_create.return_value = True

    initializer = RedisStreamInitializer(redis_client)

    await initializer.create_consumer_group()

    redis_client.xgroup_create.assert_awaited_once_with(
        "notifications", "notification-workers", mkstream=True, id="$"
    )


async def test_create_consumer_group_already_exists():
    redis_client = AsyncMock()
    redis_client.xgroup_create.side_effect = ResponseError("BUSYGROUP")

    initializer = RedisStreamInitializer(redis_client)

    await initializer.create_consumer_group()

    redis_client.xgroup_create.assert_awaited_once()


async def test_xgroup_create_incorrect():
    redis_client = AsyncMock()
    redis_client.xgroup_create.side_effect = RedisError()

    initializer = RedisStreamInitializer(redis_client)

    with pytest.raises(RedisConnectorError) as exc_info:
        await initializer.create_consumer_group()

    redis_client.xgroup_create.assert_awaited_once()

    assert isinstance(exc_info.value.__cause__, RedisError)
