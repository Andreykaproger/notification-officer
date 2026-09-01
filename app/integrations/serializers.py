from pydantic import ValidationError

from app.integrations.dto import NotificationMessage
from app.integrations.exceptions import NotificationSerializationError
from app.integrations.pydantic_models import NotificationMessageModel


class NotificationMessageSerializer:
    @staticmethod
    def to_json(notification: NotificationMessage) -> str:

        try:
            result = NotificationMessageModel.model_validate(notification)
        except ValidationError as exc:
            raise NotificationSerializationError(
                "Failed to serialize notification"
            ) from exc

        return result.model_dump_json()

    @staticmethod
    def from_json(json_message: str) -> NotificationMessage:

        try:
            model = NotificationMessageModel.model_validate_json(json_message)
            result = model.model_dump()
        except ValidationError as exc:
            raise NotificationSerializationError(
                "Failed to deserialize notification"
            ) from exc

        message = NotificationMessage(**result)
        return message
