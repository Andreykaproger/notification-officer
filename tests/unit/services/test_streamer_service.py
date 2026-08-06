from datetime import datetime

import pytest

from app.application.exceptions.streamer import (
    StreamerAlreadyExistsError,
    StreamerNotFoundError,
)
from app.domain.entities.streamer import Streamer
from app.integrations.twitch.dto import EventSubscription
from app.integrations.twitch.enums import EventSubStatus, EventSubType
from app.integrations.twitch.exceptions import (
    EventSubClientError,
    TwitchUserNotFoundError,
)


async def test_create_success(
    service,
    repository,
    uow,
    helix_client,
    eventsub_client,
    streamer,
    created_streamer,
    helix_user,
) -> None:

    event_subscription = EventSubscription(
        id="id",
        status=EventSubStatus.ENABLED,
        type=EventSubType.STREAM_ONLINE,
        created_at=datetime(2026, 7, 12),
    )

    repository.get_by_login.return_value = None
    helix_client.get_user_by_login.return_value = helix_user
    repository.create.return_value = created_streamer
    eventsub_client.create_subscription.return_value = event_subscription

    # Act
    result = await service.create(streamer)

    # Assert
    repository.get_by_login.assert_awaited_once_with(streamer.login)
    eventsub_client.create_subscription.assert_awaited_once()
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
    eventsub_client,
    created_streamer,
) -> None:

    repository.get_by_login.return_value = created_streamer

    # Act / Assert
    with pytest.raises(StreamerAlreadyExistsError):
        await service.create(created_streamer)

    repository.get_by_login.assert_awaited_once_with(created_streamer.login)
    eventsub_client.create_subscription.assert_not_awaited()
    helix_client.get_user_by_login.assert_not_awaited()
    repository.create.assert_not_awaited()

    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()


async def test_create_streamer_helix_client_not_found(
    service, repository, uow, helix_client, eventsub_client, streamer
) -> None:

    repository.get_by_login.return_value = None
    helix_client.get_user_by_login.side_effect = TwitchUserNotFoundError(streamer.login)

    # Act / Assert
    with pytest.raises(TwitchUserNotFoundError):
        await service.create(streamer)

    repository.get_by_login.assert_awaited_once_with(streamer.login)
    helix_client.get_user_by_login.assert_awaited_once_with(streamer.login)
    repository.create.assert_not_awaited()
    eventsub_client.create_subscription.assert_not_awaited()

    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()


async def test_create_streamer_eventsub_subscription_failed(
    service,
    repository,
    uow,
    helix_client,
    eventsub_client,
    streamer,
    helix_user,
    created_streamer,
):

    repository.get_by_login.return_value = None
    helix_client.get_user_by_login.return_value = helix_user
    repository.create.return_value = created_streamer
    eventsub_client.create_subscription.side_effect = EventSubClientError(
        "Helix Client error"
    )

    with pytest.raises(EventSubClientError):
        await service.create(streamer)

    repository.get_by_login.assert_awaited_once_with(streamer.login)
    helix_client.get_user_by_login.assert_awaited_once_with(streamer.login)
    eventsub_client.create_subscription.assert_awaited_once()
    args, kwargs = eventsub_client.create_subscription.await_args

    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once()

    assert kwargs["event_type"] == EventSubType.STREAM_ONLINE
    assert kwargs["condition"].broadcaster_user_id == helix_user.id


async def test_create_rollback_on_repository_error(
    service,
    repository,
    uow,
    helix_client,
    eventsub_client,
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
    eventsub_client.create_subscription.assert_not_awaited()

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

    assert exc_info.value.message == f"Streamer with {streamer_id} not found"


async def test_get_by_login_success(service, repository, uow, created_streamer):
    # Arrange
    repository.get_by_login.return_value = created_streamer

    # Act
    result = await service.get_by_login(created_streamer.login)

    # Assert
    repository.get_by_login.assert_awaited_once_with(created_streamer.login)
    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()

    assert result == created_streamer


async def test_get_by_login_not_found(service, repository, uow, created_streamer):

    # Arrange

    repository.get_by_login.return_value = None

    # Act/Assert
    with pytest.raises(StreamerNotFoundError) as exc_info:
        await service.get_by_login(created_streamer.login)

    repository.get_by_login.assert_awaited_once_with(created_streamer.login)
    uow.commit.assert_not_awaited()
    uow.rollback.assert_not_awaited()

    assert (
        exc_info.value.message
        == f"Streamer with login {created_streamer.login} not found"
    )


async def test_get_all_success(
    service,
    repository,
    uow,
    created_streamer,
) -> None:

    # Arrange
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
