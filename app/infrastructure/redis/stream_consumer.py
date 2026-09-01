import logging
from typing import cast
from uuid import uuid4

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.infrastructure.redis.dto import RedisStreamMessage
from app.infrastructure.redis.exceptions import (
    RedisConnectorError,
    RedisMessageFormatError,
)

RedisStreamResult = list[
    tuple[
        str,
        list[
            tuple[
                str,
                dict[str, str],
            ]
        ],
    ]
]


class RedisStreamConsumer:
    _STREAM_NAME = "notifications"
    _GROUP_NAME = "notification-workers"
    _BLOCK_TIMEOUT_MS = 5000

    def __init__(
        self,
        redis_client: Redis,
    ):
        self._redis_client = redis_client
        self._consumer_name = f"notification-worker-{uuid4()}"

    async def _create_message(
        self,
        message_id: str,
        data: dict[str, str],
    ) -> RedisStreamMessage:

        if "message" not in data:
            await self.ack(message_id)
            logging.error("Redis message does not contain 'message' field")
            raise RedisMessageFormatError(
                "Redis message does not contain 'message' field"
            )

        payload = data["message"]

        if not isinstance(payload, str):
            await self.ack(message_id)
            logging.error("Redis message field must be a string")
            raise RedisMessageFormatError("Redis message field must be a string")

        return RedisStreamMessage(
            message_id=message_id,
            payload=payload,
        )

    async def consume(self) -> RedisStreamMessage:
        while True:
            try:
                raw_result = await self._redis_client.xreadgroup(
                    self._GROUP_NAME,
                    self._consumer_name,
                    count=1,
                    block=self._BLOCK_TIMEOUT_MS,
                    streams={self._STREAM_NAME: ">"},
                )
            except RedisError as exc:
                raise RedisConnectorError("Failed to consume Redis message") from exc

            result: RedisStreamResult = cast(
                RedisStreamResult,
                raw_result,
            )

            for _, messages in result:
                for message_id, data in messages:
                    try:
                        message = await self._create_message(message_id, data)
                    except RedisMessageFormatError:
                        continue
                    else:
                        return message

    async def ack(
        self,
        message_id: str,
    ) -> None:
        try:
            await self._redis_client.xack(
                self._STREAM_NAME,
                self._GROUP_NAME,
                message_id,
            )
        except RedisError as exc:
            raise RedisConnectorError("Failed to acknowledge Redis message") from exc

    async def reclaim_pending(
        self,
        min_idle_time_ms: int,
        count: int,
    ) -> list[RedisStreamMessage]:
        try:
            _, messages, _ = await self._redis_client.xautoclaim(
                self._STREAM_NAME,
                self._GROUP_NAME,
                self._consumer_name,
                min_idle_time=min_idle_time_ms,
                count=count,
                start_id="0-0",
            )
        except RedisError as exc:
            raise RedisConnectorError("Failed to reclaim Redis message") from exc

        redis_messages = []

        for msg_id, fields in messages:
            try:
                mes = await self._create_message(msg_id, fields)
                redis_messages.append(mes)
            except RedisMessageFormatError:
                continue

        return redis_messages
