from typing import cast

from fastapi import Depends, Request

from app.application.handlers.registry import HandlerRegistry
from app.application.workers.notification_worker import NotificationWorker
from app.dependencies.redis import get_redis_consumer
from app.infrastructure.redis.stream_consumer import RedisStreamConsumer


def get_handler_registry(request: Request) -> HandlerRegistry:
    return cast(HandlerRegistry, request.app.state.registry)


def get_notification_worker(
    consumer: RedisStreamConsumer = Depends(get_redis_consumer),
    handler_registry: HandlerRegistry = Depends(get_handler_registry),
) -> NotificationWorker:
    return NotificationWorker(consumer, handler_registry)
