from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from starlette.responses import PlainTextResponse, Response

from app.application.services.eventsub_service import EventSubWebhookService
from app.dependencies.twitch import get_event_sub_service
from app.integrations.twitch.dto import EventSubWebhookRequest
from app.integrations.twitch.enums import EventSubMessageType

eventsub_router = APIRouter()


@eventsub_router.post("/twitch/webhook")
async def twitch_webhook(
    request: Request,
    message_type: Annotated[
        EventSubMessageType, Header(alias="Twitch-Eventsub-Message-Type")
    ],
    message_id: str = Header(alias="Twitch-Eventsub-Message-Id"),
    timestamp: str = Header(alias="Twitch-Eventsub-Message-Timestamp"),
    signature: str = Header(alias="Twitch-Eventsub-Message-Signature"),
    service: EventSubWebhookService = Depends(get_event_sub_service),
):
    body = await request.body()

    dto = EventSubWebhookRequest(
        request_body=body,
        message_type=message_type,
        message_id=message_id,
        timestamp=timestamp,
        signature=signature,
    )

    result = await service.handle(dto)

    if result is not None:
        return PlainTextResponse(result)

    return Response(status_code=204)
