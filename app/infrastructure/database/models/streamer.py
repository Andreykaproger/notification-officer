from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class StreamerModel(Base):
    __tablename__ = "streamers"

    id: Mapped[int] = mapped_column(primary_key=True)

    twitch_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
    )

    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
