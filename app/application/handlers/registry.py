from app.application.exceptions.handler import NotificationHandlerNotFound
from app.application.handlers.protocol import NotificationHandlerProtocol


class HandlerRegistry:
    def __init__(
        self,
        handlers: dict[str, NotificationHandlerProtocol],
    ) -> None:
        self._handlers = handlers

    def get(
        self,
        platform: str,
    ) -> NotificationHandlerProtocol:
        try:
            handler = self._handlers[platform]
        except KeyError as exc:
            raise NotificationHandlerNotFound() from exc

        return handler
