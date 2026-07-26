from datetime import datetime

from pydantic import BaseModel, Field


class CreateStreamerRequest(BaseModel):
    login: str = Field(
        min_length=1,
        max_length=25,
    )
    display_name: str


class StreamerResponse(BaseModel):
    id: int
    twitch_id: str
    login: str
    display_name: str
    created_at: datetime
