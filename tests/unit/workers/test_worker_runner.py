import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.workers.worker_runner import WorkerRunner
from app.infrastructure.redis.dto import RedisStreamMessage
from app.infrastructure.redis.exceptions import RedisConnectorError


async def test_run_two_messages_until_shutdown():
    factory = Mock()
    worker = AsyncMock()
    shutdown_event = Mock()
    worker.process_message.side_effect = [None, None]
    shutdown_event.is_set.side_effect = [
        False,
        False,
        True,
    ]
    factory.create.return_value = worker

    worker_runner = WorkerRunner(factory, shutdown_event)

    await worker_runner.run()

    assert worker.process_message.await_count == 2
    assert shutdown_event.is_set.call_count == 3

    factory.create.assert_called_once_with()


async def test_run_stops_after_shutdown_event():
    factory = Mock()
    worker = AsyncMock()
    shutdown_event = Mock()
    worker.process_message.side_effect = [
        RedisStreamMessage(
            message_id="1234",
            payload="""
            {"platform": "invalid_platform", 
            "event_type": "stream.online", 
            "payload": {"payload": "payload"}}""".strip(),
        ),
        RedisStreamMessage(
            message_id="1235",
            payload="""
            {"platform": "twitch", 
            "event_type": "stream.online", 
            "payload": {"payload": "payload"}}""".strip(),
        ),
        RedisStreamMessage(
            message_id="1236",
            payload="""
            {"platform": "twitch", 
            "event_type": "stream.online", 
            "payload": {"payload": "payload"}}""".strip(),
        ),
    ]
    shutdown_event.is_set.side_effect = [
        False,
        False,
        True,
    ]
    factory.create.return_value = worker

    worker_runner = WorkerRunner(factory, shutdown_event)

    await worker_runner.run()

    assert worker.process_message.await_count == 2
    assert shutdown_event.is_set.call_count == 3

    factory.create.assert_called_once()


async def test_run_reload_after_redis_error_in_worker():
    factory = Mock()
    worker1 = AsyncMock()
    worker2 = AsyncMock()
    shutdown_event = Mock()
    shutdown_event.wait = AsyncMock()

    worker1.process_message.side_effect = [
        RedisStreamMessage(
            message_id="1234",
            payload="""
            {"platform": "invalid_platform",
            "event_type": "stream.online",
            "payload": {"payload": "payload"}}""".strip(),
        ),
        RedisConnectorError(),
    ]
    worker2.process_message.side_effect = [
        RedisStreamMessage(
            message_id="1235",
            payload="""
            {"platform": "twitch",
            "event_type": "stream.online",
            "payload": {"payload": "payload"}}""".strip(),
        ),
    ]
    shutdown_event.is_set.side_effect = [
        False,
        False,
        False,
        True,
    ]
    factory.create.side_effect = [
        worker1,
        worker2,
    ]
    shutdown_event.wait.side_effect = asyncio.TimeoutError

    worker_runner = WorkerRunner(factory, shutdown_event)

    await worker_runner.run()

    assert worker1.process_message.await_count == 2
    assert worker2.process_message.await_count == 1
    assert shutdown_event.is_set.call_count == 4
    assert factory.create.call_count == 2

    worker1.reclaim_pending.assert_not_awaited()
    worker2.reclaim_pending.assert_awaited_once()
    shutdown_event.wait.assert_awaited_once()


async def test_run_raises_when_reclaim_pending_fails():
    factory = Mock()
    worker1 = AsyncMock()
    worker2 = AsyncMock()
    shutdown_event = Mock()
    shutdown_event.wait = AsyncMock()

    worker1.process_message.side_effect = [
        RedisStreamMessage(
            message_id="1234",
            payload="""
            {"platform": "invalid_platform", 
            "event_type": "stream.online", 
            "payload": {"payload": "payload"}}""".strip(),
        ),
        RedisConnectorError(),
    ]
    shutdown_event.is_set.side_effect = [
        False,
        False,
    ]
    shutdown_event.wait.side_effect = asyncio.TimeoutError
    factory.create.side_effect = [
        worker1,
        worker2,
    ]
    worker1.reclaim_pending.side_effect = RedisConnectorError()
    worker2.reclaim_pending.side_effect = RedisConnectorError()

    worker_runner = WorkerRunner(factory, shutdown_event)

    with pytest.raises(RedisConnectorError):
        await worker_runner.run()

    assert shutdown_event.is_set.call_count == 2
    assert worker1.process_message.await_count == 2
    assert factory.create.call_count == 2

    worker1.reclaim_pending.assert_not_awaited()
    worker2.reclaim_pending.assert_awaited_once()
    worker2.process_message.assert_not_awaited()
