from typing import Protocol

from app.integrations.dto import NotificationMessage


class NotificationHandlerProtocol(Protocol):
    def handle(
        self,
        notification: NotificationMessage,
    ) -> None:
        """Handle message notification"""
        pass
