from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.exceptions.streamer import (
    StreamerAlreadyExistsError,
    StreamerNotFoundError,
)
from app.application.services.streamer_service import StreamerService
from app.domain.entities.streamer import Streamer


async def test_create_success() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    streamer = Streamer(
        id=None,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
        created_at=None,
    )

    created_streamer = Streamer(
        id=1,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
        created_at=datetime(2026, 7, 22, 12, 0, 0),
    )

    repository.get_by_login.return_value = None
    repository.create.return_value = created_streamer

    service = StreamerService(repository, uow)

    # Act
    result = await service.create(streamer)

    # Assert
    repository.get_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_awaited_once_with(streamer)

    uow.commit.assert_awaited_once_with()
    uow.rollback.assert_not_awaited()

    assert result == created_streamer


async def test_create_streamer_already_exists() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    streamer = Streamer(
        id=None,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
        created_at=None,
    )

    repository.get_by_login.return_value = streamer

    service = StreamerService(repository, uow)

    # Act / Assert
    with pytest.raises(StreamerAlreadyExistsError):
        await service.create(streamer)

    repository.get_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_not_awaited()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()


async def test_create_rollback_on_repository_error() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    streamer = Streamer(
        id=None,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
        created_at=None,
    )

    class RepositoryError(Exception):
        pass

    repository.get_by_login.return_value = None
    repository.create.side_effect = RepositoryError("Database error")

    service = StreamerService(repository, uow)

    # Act / Assert
    with pytest.raises(RepositoryError):
        await service.create(streamer)

    repository.get_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_awaited_once_with(streamer)
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once()


async def test_get_by_id_success() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    streamer_id = 1

    streamer = Streamer(
        id=streamer_id,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
    )

    repository.get_by_id.return_value = streamer
    service = StreamerService(repository, uow)

    # Act
    result = await service.get_by_id(streamer_id)

    # Assert
    repository.get_by_id.assert_awaited_once_with(streamer_id)

    assert result == streamer


async def test_get_by_id_not_found() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    streamer_id = 1

    repository.get_by_id.return_value = None

    service = StreamerService(repository, uow)

    # Act
    with pytest.raises(StreamerNotFoundError) as exc_info:
        await service.get_by_id(streamer_id)

    # Assert
    repository.get_by_id.assert_awaited_once_with(streamer_id)

    assert exc_info.value.streamer_id == streamer_id
    assert str(exc_info.value) == f"Streamer {streamer_id} not found"


async def test_get_all_success() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    streamers = [
        Streamer(
            id=1,
            twitch_id="123456",
            login="shroud",
            display_name="Shroud",
            created_at=datetime(2026, 7, 22, 12, 0, 0),
        )
    ]

    service = StreamerService(repository, uow)
    repository.get_all.return_value = streamers

    # Act
    result = await service.get_all()

    # Assert
    repository.get_all.assert_awaited_once()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()

    assert result == streamers


async def test_get_all_empty() -> None:
    # Arrange
    repository = AsyncMock()
    uow = AsyncMock()

    empty_streamers: list[Streamer] = []

    repository.get_all.return_value = empty_streamers

    service = StreamerService(repository, uow)

    # Act
    result = await service.get_all()

    # Assert
    repository.get_all.assert_awaited_once()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()

    assert result == empty_streamers
