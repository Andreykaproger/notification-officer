from fastapi import Depends

from app.application.publishers.notification_publisher import NotificationPublisher
from app.dependencies.redis import get_redis_connector
from app.infrastructure.redis.connector import RedisConnector


def get_notification_publisher(
    redis_connector: RedisConnector = Depends(get_redis_connector),
) -> NotificationPublisher:
    return NotificationPublisher(redis_connector)
