import json

import pytest

from app.integrations.exceptions import NotificationSerializationError
from app.integrations.serializers import NotificationMessageSerializer


def test_message_serializer_to_json_correct(
    notification_message, dict_notification_message
):

    result = NotificationMessageSerializer.to_json(notification_message)

    actual = json.loads(result)

    expected = dict_notification_message

    assert actual == expected


def test_message_serializer_to_json_incorrect(
    invalid_notification_message,
):
    with pytest.raises(NotificationSerializationError) as exc_info:
        NotificationMessageSerializer.to_json(invalid_notification_message)

    assert str(exc_info.value) == "Failed to serialize notification"


def test_message_serializer_from_json_correct(
    dict_notification_message,
    notification_message,
):
    message = json.dumps(dict_notification_message)

    result = NotificationMessageSerializer.from_json(message)

    assert result == notification_message


def test_message_serializer_from_json_mixed_fields(
    notification_message,
):
    message = json.dumps(
        {
            "event_type": "test",
            "payload": {
                "message": "test message",
            },
            "platform": "test",
        }
    )

    result = NotificationMessageSerializer.from_json(message)

    assert result == notification_message


def test_message_serializer_from_json_invalid_json():
    invalid_json = """{
            "platform": "test",
            "event_type": "test",
            "payload": {}
            something strange
        }
    """

    with pytest.raises(NotificationSerializationError) as exc_info:
        NotificationMessageSerializer.from_json(invalid_json)

    assert str(exc_info.value) == "Failed to deserialize notification"


def test_message_serializer_from_json_missing_field(
    dict_notification_message,
):
    dict_notification_message.pop("payload")
    invalid_message = json.dumps(dict_notification_message)

    with pytest.raises(NotificationSerializationError):
        NotificationMessageSerializer.from_json(invalid_message)


def test_message_serializer_from_json_extra_field(
    dict_notification_message,
):
    dict_notification_message["extra_field"] = "test"
    invalid_message = json.dumps(dict_notification_message)

    with pytest.raises(NotificationSerializationError):
        NotificationMessageSerializer.from_json(invalid_message)


def test_message_serializer_from_json_incorrect_field_type(dict_notification_message):
    dict_notification_message["payload"] = "test"
    incorrect_message = json.dumps(dict_notification_message)

    with pytest.raises(NotificationSerializationError):
        NotificationMessageSerializer.from_json(incorrect_message)


def test_message_serializer_round_trip(notification_message):

    serialize = NotificationMessageSerializer.to_json(notification_message)
    deserialize = NotificationMessageSerializer.from_json(serialize)

    assert deserialize == notification_message
