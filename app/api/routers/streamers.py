from fastapi import APIRouter, Depends

from app.api.mappers.streamer_mapper import StreamerApiMapper
from app.api.schemas.streamer import CreateStreamerRequest, StreamerResponse
from app.application.services.streamer_service import StreamerService
from app.dependencies.streamers import get_streamer_service

streamers_router = APIRouter(
    prefix="/streamers",
)


@streamers_router.post(
    "",
    status_code=201,
    response_model=StreamerResponse,
)
async def create_streamer(
    request: CreateStreamerRequest,
    service: StreamerService = Depends(get_streamer_service),
) -> StreamerResponse:

    streamer = StreamerApiMapper.to_domain(request)

    created_streamer = await service.create(streamer)

    return StreamerApiMapper.to_response(created_streamer)


@streamers_router.get(
    "/{streamer_id}",
    status_code=200,
    response_model=StreamerResponse,
)
async def get_streamer_by_id(
    streamer_id: int, service: StreamerService = Depends(get_streamer_service)
) -> StreamerResponse:
    streamer = await service.get_by_id(streamer_id)

    return StreamerApiMapper.to_response(streamer)


@streamers_router.get(
    "/login/{streamer_login}",
    status_code=200,
    response_model=StreamerResponse,
)
async def get_streamer_by_login(
    streamer_login: str, service: StreamerService = Depends(get_streamer_service)
) -> StreamerResponse:
    streamer = await service.get_by_login(streamer_login)

    return StreamerApiMapper.to_response(streamer)


@streamers_router.get(
    "",
    status_code=200,
    response_model=list[StreamerResponse],
)
async def get_all_streamers(
    service: StreamerService = Depends(get_streamer_service),
) -> list[StreamerResponse]:

    streamers = await service.get_all()

    return [StreamerApiMapper.to_response(streamer) for streamer in streamers]
