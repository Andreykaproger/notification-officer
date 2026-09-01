from typing import cast

from fastapi import Depends, Request
from redis.asyncio import Redis

from app.infrastructure.redis.connector import RedisConnector
from app.infrastructure.redis.stream_consumer import RedisStreamConsumer
from app.infrastructure.redis.stream_initializer import RedisStreamInitializer


def get_redis_client(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


def get_redis_connector(
    redis_client: Redis = Depends(get_redis_client),
) -> RedisConnector:
    return RedisConnector(redis_client=redis_client)


def get_redis_consumer(
    redis_client: Redis = Depends(get_redis_client),
) -> RedisStreamConsumer:
    return RedisStreamConsumer(redis_client=redis_client)


def get_redis_initializer(
    redis_client: Redis = Depends(get_redis_client),
) -> RedisStreamInitializer:
    return RedisStreamInitializer(redis_client=redis_client)
