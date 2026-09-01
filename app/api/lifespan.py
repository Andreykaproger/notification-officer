import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.application.handlers.registry import HandlerRegistry
from app.application.handlers.twitch import TwitchHandler
from app.application.workers.worker_factory import WorkerFactory
from app.application.workers.worker_runner import WorkerRunner
from app.core.config import get_settings
from app.infrastructure import my_redis
from app.infrastructure.redis.stream_initializer import RedisStreamInitializer


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.http_client = httpx.AsyncClient()
    app.state.redis = await my_redis.connect(settings)

    shutdown_event = asyncio.Event()
    twitch_handler = TwitchHandler()
    app.state.registry = HandlerRegistry(
        {
            "twitch": twitch_handler,
        }
    )

    consumer_group = RedisStreamInitializer(app.state.redis)
    await consumer_group.create_consumer_group()

    factory = WorkerFactory(
        redis_client=app.state.redis,
        registry=app.state.registry,
    )

    worker_runner = WorkerRunner(
        factory=factory,
        shutdown_event=shutdown_event,
    )

    app.state.worker_runner = worker_runner
    app.state.worker_task = asyncio.create_task(worker_runner.run())

    yield

    try:
        shutdown_event.set()
        await app.state.worker_task
    finally:
        await my_redis.disconnect(app.state.redis)
        await app.state.http_client.aclose()
