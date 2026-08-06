import hashlib
import hmac

from app.integrations.twitch.exceptions import InvalidTwitchSignatureError


class TwitchSignatureVerifier:
    _HMAC_PREFIX = "sha256="

    def __init__(
        self,
        secret: str,
    ) -> None:
        self._secret = secret.encode("utf-8")

    def verify(
        self, message_id: str, timestamp: str, body: bytes, signature: str
    ) -> None:

        message = message_id.encode("utf-8") + timestamp.encode("utf-8") + body
        key = self._secret

        calculated_signature = (
            self._HMAC_PREFIX + hmac.new(key, message, hashlib.sha256).hexdigest()
        )

        if not hmac.compare_digest(calculated_signature, signature):
            raise InvalidTwitchSignatureError()
