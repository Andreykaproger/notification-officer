from redis.asyncio import Redis

from app.core.config import Settings


async def connect(settings: Settings):
    client = Redis(
        host=settings.redis_host, port=settings.redis_port, decode_responses=True
    )

    return client


async def disconnect(connection):
    await connection.close()
