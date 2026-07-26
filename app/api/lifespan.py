from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.infrastructure import my_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.redis = await my_redis.connect(settings)

    yield

    await my_redis.disconnect(app.state.redis)
