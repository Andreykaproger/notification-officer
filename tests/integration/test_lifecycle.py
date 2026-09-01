from unittest.mock import AsyncMock

from fastapi import FastAPI

from app.api.lifespan import lifespan
from app.infrastructure import my_redis


async def test_lifecycle(
    monkeypatch,
    clean_redis,
):

    app = FastAPI(lifespan=lifespan)
    disconnect = AsyncMock()

    monkeypatch.setattr(my_redis, "disconnect", disconnect)

    async with app.router.lifespan_context(app):
        assert not app.state.http_client.is_closed

        assert app.state.redis is not None
        assert await app.state.redis.ping()

        assert app.state.registry is not None
        assert app.state.worker_runner is not None

        assert not app.state.worker_task.done()

        groups = await app.state.redis.xinfo_groups("notifications")

        assert any(group["name"] == "notification-workers" for group in groups)

    assert app.state.worker_task.done()
    assert app.state.worker_task.exception() is None
    assert app.state.http_client.is_closed
    disconnect.assert_awaited_once_with(
        app.state.redis,
    )
