import hashlib
import hmac

import pytest

from app.integrations.twitch.exceptions import InvalidTwitchSignatureError
from app.integrations.twitch.verifier import TwitchSignatureVerifier


def test_verify_valid_signature():
    secret = "secret"
    verifier = TwitchSignatureVerifier(secret)

    body = b"body"
    message_id = "message_id"
    timestamp = "timestamp"
    message = message_id.encode("utf-8") + timestamp.encode("utf-8") + body

    # Simulates Twitch HMAC signature generation.
    signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()
    )

    verifier.verify(
        message_id=message_id,
        timestamp=timestamp,
        body=body,
        signature=signature,
    )


def test_verify_invalid_signature():
    secret = "secret"
    verifier = TwitchSignatureVerifier(secret)

    body = b"body"
    message_id = "message_id"
    timestamp = "timestamp"
    message = message_id.encode("utf-8") + timestamp.encode("utf-8") + body
    wrong_secret = "wrong_secret"

    # Simulates Twitch HMAC signature generation.
    invalid_signature = (
        "sha256="
        + hmac.new(
            wrong_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()
    )

    with pytest.raises(InvalidTwitchSignatureError) as exc:
        verifier.verify(
            message_id=message_id,
            timestamp=timestamp,
            body=body,
            signature=invalid_signature,
        )

    assert str(exc.value) == "Invalid Twitch webhook signature"
