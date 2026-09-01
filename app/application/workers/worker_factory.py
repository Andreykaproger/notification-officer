from redis.asyncio import Redis

from app.application.handlers.registry import HandlerRegistry
from app.application.workers.notification_worker import NotificationWorker
from app.infrastructure.redis.stream_consumer import RedisStreamConsumer


class WorkerFactory:
    def __init__(self, redis_client: Redis, registry: HandlerRegistry) -> None:
        self._redis_client = redis_client
        self._registry = registry

    def create(self) -> NotificationWorker:
        consumer = RedisStreamConsumer(self._redis_client)

        return NotificationWorker(consumer=consumer, handler_registry=self._registry)
