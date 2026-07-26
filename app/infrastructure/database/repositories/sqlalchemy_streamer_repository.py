from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.streamer import Streamer
from app.infrastructure.database.models import StreamerModel
from app.infrastructure.mappers.streamer_mapper import StreamerMapper


class SQLAlchemyStreamerRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, streamer: Streamer) -> Streamer:
        model = StreamerMapper.to_orm(streamer)

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return StreamerMapper.to_domain(model)

    async def get_by_id(self, streamer_id: int) -> Streamer | None:

        stmt = select(StreamerModel).where(StreamerModel.id == streamer_id)

        result = await self._session.execute(stmt)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return StreamerMapper.to_domain(model)

    async def get_by_login(self, login: str) -> Streamer | None:

        stmt = select(StreamerModel).where(StreamerModel.login == login)

        result = await self._session.execute(stmt)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return StreamerMapper.to_domain(model)

    async def get_all(self) -> list[Streamer]:
        stmt = select(StreamerModel)

        result = await self._session.execute(stmt)

        models = result.scalars().all()

        return [StreamerMapper.to_domain(model) for model in models]
