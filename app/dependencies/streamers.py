from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.streamer_service import StreamerService
from app.application.unit_of_work import UnitOfWork
from app.dependencies.twitch import get_helix_client
from app.domain.repositories.streamer_repository import StreamerRepository
from app.infrastructure.database.repositories.sqlalchemy_streamer_repository import (
    SQLAlchemyStreamerRepository,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.unit_of_work.sqlalchemy import SQLAlchemyUnitOfWork
from app.integrations.twitch.helix_client import HelixClient


def get_streamer_repository(
    session: AsyncSession = Depends(get_session),
) -> SQLAlchemyStreamerRepository:
    return SQLAlchemyStreamerRepository(session)


def get_unit_of_work(session: AsyncSession = Depends(get_session)) -> UnitOfWork:
    return SQLAlchemyUnitOfWork(session)


def get_streamer_service(
    repository: StreamerRepository = Depends(get_streamer_repository),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    helix_client: HelixClient = Depends(get_helix_client),
) -> StreamerService:
    return StreamerService(repository, unit_of_work, helix_client)
