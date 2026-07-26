from typing import Protocol

from app.domain.entities.streamer import Streamer


class StreamerRepository(Protocol):
    async def create(self, streamer: Streamer) -> Streamer:
        """Create a new streamer."""
        pass

    async def get_by_id(self, streamer_id: int) -> Streamer | None:
        """Return streamer by id."""
        pass

    async def get_by_login(self, login: str) -> Streamer | None:
        """Return streamer by login."""
        pass

    async def get_all(self) -> list[Streamer]:
        """Return all streamers."""
        pass
