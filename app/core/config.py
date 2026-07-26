from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    All configuration is loaded from environment variables
    or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application

    app_name: str = "Notification Officer"
    environment: str = "development"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database

    postgres_host: str = Field(
        ...,
        description="Postgres host",
    )
    postgres_port: int = Field(
        ...,
        description="Postgres port",
    )
    postgres_db: str = Field(
        ...,
        description="Postgres database",
    )
    postgres_user: str = Field(
        ...,
        description="Postgres user",
    )
    postgres_password: str = Field(
        ...,
        description="Postgres password",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    # Redis

    redis_host: str = Field(
        ...,
        description="Redis connection URL",
    )
    redis_port: int = Field(
        ...,
        description="Redis connection port",
    )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    # Twitch

    twitch_client_id: str = Field(
        ...,
        description="Twitch Client ID",
    )
    twitch_client_secret: str = Field(
        ...,
        description="Twitch Client Secret",
    )
    twitch_webhook_secret: str = Field(
        ...,
        description="Secret used to verify EventSub webhooks",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return application settings.

    The settings object is created only once
    during the application lifetime.
    """
    return Settings()


settings = get_settings()
