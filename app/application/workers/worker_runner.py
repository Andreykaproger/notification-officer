import asyncio
import logging

from app.application.workers.worker_factory import WorkerFactory
from app.infrastructure.redis.exceptions import RedisConnectorError

logger = logging.getLogger(__name__)


class WorkerRunner:
    RESTART_DELAY = 5

    def __init__(
        self,
        factory: WorkerFactory,
        shutdown_event: asyncio.Event,
    ) -> None:
        self._factory = factory
        self._shutdown_event = shutdown_event

    async def run(self) -> None:
        worker = self._factory.create()

        while not self._shutdown_event.is_set():
            try:
                await worker.process_message()
            except RedisConnectorError:
                logger.exception("Redis connection error")
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(), self.RESTART_DELAY
                    )
                except asyncio.TimeoutError:
                    worker = self._factory.create()
                    await worker.reclaim_pending()
