from app.application.exceptions.base import PermanentNotificationError


class NotificationHandlerNotFound(PermanentNotificationError):
    def __init__(self, message: str = "Platform with this name does not support"):
        super().__init__(message)
