from typing import cast

import httpx
from fastapi import Depends, Request

from app.application.services.eventsub_service import EventSubWebhookService
from app.core.config import Settings, get_settings
from app.integrations.twitch.auth import TwitchAuthClient
from app.integrations.twitch.eventsub_client import EventSubClient
from app.integrations.twitch.helix_client import HelixClient
from app.integrations.twitch.verifier import TwitchSignatureVerifier


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


async def get_twitch_auth_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
) -> TwitchAuthClient:
    return TwitchAuthClient(
        http_client=http_client,
        settings=settings,
    )


async def get_event_sub_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    auth_client: TwitchAuthClient = Depends(get_twitch_auth_client),
    settings: Settings = Depends(get_settings),
) -> EventSubClient:
    return EventSubClient(
        http_client=http_client,
        auth_client=auth_client,
        settings=settings,
    )


async def get_helix_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    auth_client: TwitchAuthClient = Depends(get_twitch_auth_client),
    settings: Settings = Depends(get_settings),
) -> HelixClient:
    return HelixClient(
        http_client=http_client,
        auth_client=auth_client,
        settings=settings,
    )


async def get_twitch_webhook_verifier(
    settings: Settings = Depends(get_settings),
) -> TwitchSignatureVerifier:
    secret = settings.twitch_webhook_secret
    return TwitchSignatureVerifier(secret)


async def get_event_sub_service(
    verifier: TwitchSignatureVerifier = Depends(get_twitch_webhook_verifier),
) -> EventSubWebhookService:
    return EventSubWebhookService(verifier)
