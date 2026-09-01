from app.application.exceptions.base import PermanentNotificationError


class NotificationSerializationError(PermanentNotificationError):
    """Raised when appears errors with notification serialization."""

    def __init__(self, message: str = "Notification serialization error"):
        super().__init__(message)
