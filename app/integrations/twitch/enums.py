from enum import StrEnum


class EventSubType(StrEnum):
    STREAM_ONLINE = "stream.online"
    STREAM_OFFLINE = "stream.offline"
    CHANNEL_UPDATE = "channel.update"


class EventSubStatus(StrEnum):
    ENABLED = "enabled"
    WEBHOOK_CALLBACK_VERIFICATION_PENDING = "webhook_callback_verification_pending"


class EventSubMessageType(StrEnum):
    WEBHOOK_CALLBACK_VERIFICATION = "webhook_callback_verification"
    NOTIFICATION = "notification"
    REVOCATION = "revocation"
