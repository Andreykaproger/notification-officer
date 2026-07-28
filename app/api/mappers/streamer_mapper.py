from app.api.schemas.streamer import CreateStreamerRequest, StreamerResponse
from app.domain.entities.streamer import Streamer


class StreamerApiMapper:
    @staticmethod
    def to_domain(request: CreateStreamerRequest) -> Streamer:
        return Streamer(
            id=None,
            twitch_id=None,  # type: ignore[attr-defined]
            login=request.login,
            display_name=request.display_name,
            created_at=None,
        )

    @staticmethod
    def to_response(streamer: Streamer) -> StreamerResponse:
        assert streamer.id is not None
        assert streamer.created_at is not None

        return StreamerResponse(
            id=streamer.id,
            twitch_id=streamer.twitch_id,
            login=streamer.login,
            display_name=streamer.display_name,
            created_at=streamer.created_at,
        )
