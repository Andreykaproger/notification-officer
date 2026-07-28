from app.application.exceptions import (
    StreamerAlreadyExistsError,
    StreamerNotFoundError,
)
from app.application.unit_of_work import UnitOfWork
from app.domain.entities.streamer import Streamer
from app.domain.repositories.streamer_repository import StreamerRepository
from app.integrations.twitch.helix_client import HelixClient


class StreamerService:
    def __init__(
        self, repository: StreamerRepository, uow: UnitOfWork, helix_client: HelixClient
    ):
        self._repository = repository
        self._uow = uow
        self._helix_client = helix_client

    async def create(self, streamer: Streamer):

        existing = await self._repository.get_by_login(streamer.login)

        if existing is not None:
            raise StreamerAlreadyExistsError(streamer.login)

        twitch_user = await self._helix_client.get_user_by_login(streamer.login)

        streamer.twitch_id = twitch_user.id

        try:
            model = await self._repository.create(streamer)
            await self._uow.commit()
            return model
        except Exception:
            await self._uow.rollback()
            raise

    async def get_by_id(self, streamer_id: int) -> Streamer:

        streamer = await self._repository.get_by_id(streamer_id)

        if streamer is None:
            raise StreamerNotFoundError(streamer_id)

        return streamer

    async def get_all(self) -> list[Streamer]:
        return await self._repository.get_all()
