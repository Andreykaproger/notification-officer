from app.application.exceptions.base import PermanentNotificationError


class RedisConnectorError(Exception):
    def __init__(self, message: str = "Failed to execute Redis command"):
        super().__init__(message)


class RedisMessageFormatError(PermanentNotificationError):
    def __init__(self, message: str):
        super().__init__(message)
