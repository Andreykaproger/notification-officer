from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.services.streamer_service import StreamerService
from app.domain.entities.streamer import Streamer
from app.integrations.twitch.dto import HelixUser


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def uow():
    return AsyncMock()


@pytest.fixture
def helix_client():
    return AsyncMock()


@pytest.fixture
def service(
    repository,
    uow,
    helix_client,
):
    return StreamerService(
        repository=repository,
        uow=uow,
        helix_client=helix_client,
    )


@pytest.fixture
def streamer():
    return Streamer(
        id=None,
        twitch_id=None,
        login="shroud",
        display_name="Shroud",
        created_at=None,
    )


@pytest.fixture
def created_streamer():
    return Streamer(
        id=1,
        twitch_id="123456",
        login="shroud",
        display_name="Shroud",
        created_at=datetime(2026, 7, 22, 12, 0, 0),
    )


@pytest.fixture
def helix_user():
    return HelixUser(
        id="123456",
        login="shroud",
        display_name="Shroud",
    )
