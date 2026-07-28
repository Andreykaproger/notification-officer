import pytest

from app.application.exceptions.streamer import (
    StreamerAlreadyExistsError,
    StreamerNotFoundError,
)
from app.domain.entities.streamer import Streamer
from app.integrations.twitch.exceptions import TwitchUserNotFoundError


async def test_create_success(
    service,
    repository,
    uow,
    helix_client,
    streamer,
    created_streamer,
    helix_user,
) -> None:

    repository.get_by_login.return_value = None

    helix_client.get_user_by_login.return_value = helix_user
    repository.create.return_value = created_streamer

    # Act
    result = await service.create(streamer)

    # Assert
    repository.get_by_login.assert_awaited_once_with(streamer.login)
    helix_client.get_user_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_awaited_once_with(streamer)

    uow.commit.assert_awaited_once()
    uow.rollback.assert_not_awaited()

    assert helix_user.id == streamer.twitch_id
    assert result == created_streamer


async def test_create_streamer_already_exists(
    service,
    repository,
    uow,
    helix_client,
    created_streamer,
) -> None:

    repository.get_by_login.return_value = created_streamer

    # Act / Assert
    with pytest.raises(StreamerAlreadyExistsError):
        await service.create(created_streamer)

    repository.get_by_login.assert_awaited_once_with(created_streamer.login)
    helix_client.get_user_by_login.assert_not_awaited()
    repository.create.assert_not_awaited()

    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()


async def test_create_streamer_helix_client_not_found(
    service, repository, uow, helix_client, streamer
) -> None:

    repository.get_by_login.return_value = None
    helix_client.get_user_by_login.side_effect = TwitchUserNotFoundError(streamer.login)

    # Act / Assert
    with pytest.raises(TwitchUserNotFoundError):
        await service.create(streamer)

    repository.get_by_login.assert_awaited_once_with(streamer.login)
    helix_client.get_user_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_not_awaited()

    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()


async def test_create_rollback_on_repository_error(
    service,
    repository,
    uow,
    helix_client,
    streamer,
    helix_user,
) -> None:

    class RepositoryError(Exception):
        pass

    repository.get_by_login.return_value = None
    repository.create.side_effect = RepositoryError("Database error")
    helix_client.get_user_by_login.return_value = helix_user

    # Act / Assert
    with pytest.raises(RepositoryError):
        await service.create(streamer)

    repository.get_by_login.assert_awaited_once_with(streamer.login)
    helix_client.get_user_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_awaited_once_with(streamer)

    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once()


async def test_get_by_id_success(
    service,
    repository,
    created_streamer,
) -> None:

    # Arrange

    repository.get_by_id.return_value = created_streamer

    # Act
    result = await service.get_by_id(created_streamer.id)

    # Assert
    repository.get_by_id.assert_awaited_once_with(created_streamer.id)

    assert result == created_streamer


async def test_get_by_id_not_found(
    service,
    repository,
) -> None:

    streamer_id = 1

    repository.get_by_id.return_value = None

    # Act
    with pytest.raises(StreamerNotFoundError) as exc_info:
        await service.get_by_id(streamer_id)

    # Assert
    repository.get_by_id.assert_awaited_once_with(streamer_id)

    assert exc_info.value.streamer_id == streamer_id
    assert str(exc_info.value) == f"Streamer {streamer_id} not found"


async def test_get_all_success(
    service,
    repository,
    uow,
    created_streamer,
) -> None:

    streamers = [
        created_streamer,
    ]

    repository.get_all.return_value = streamers

    # Act
    result = await service.get_all()

    # Assert
    repository.get_all.assert_awaited_once()

    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()

    assert result == streamers


async def test_get_all_empty(
    service,
    repository,
    uow,
) -> None:

    empty_streamers: list[Streamer] = []

    repository.get_all.return_value = empty_streamers

    # Act
    result = await service.get_all()

    # Assert
    repository.get_all.assert_awaited_once()

    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()

    assert result == empty_streamers
