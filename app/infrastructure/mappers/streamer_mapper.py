from app.domain.entities.streamer import Streamer
from app.infrastructure.database.models.streamer import StreamerModel


class StreamerMapper:
    """Maps Streamer domain entities to ORM models and back."""

    @staticmethod
    def to_domain(model: StreamerModel) -> Streamer:
        return Streamer(
            id=model.id,
            twitch_id=model.twitch_id,
            login=model.login,
            display_name=model.display_name,
            created_at=model.created_at,
        )

    @staticmethod
    def to_orm(streamer: Streamer) -> StreamerModel:
        return StreamerModel(
            twitch_id=streamer.twitch_id,
            login=streamer.login,
            display_name=streamer.display_name,
        )
