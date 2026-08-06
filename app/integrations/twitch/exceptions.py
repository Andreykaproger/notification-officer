class TwitchError(Exception):
    """Base exception for Twitch integration."""

    pass


class TwitchApiError(TwitchError):
    """Base exception for API Twitch integration."""

    def __init__(self, message: str) -> None:
        super().__init__(message)

    pass


class EventSubClientError(TwitchError):
    """Base exception for Helix integration."""

    def __ini__(self, message: str) -> None:
        super().__init__(message)


class TwitchAuthenticationError(TwitchApiError):
    def __init__(self) -> None:
        super().__init__("Failed to authenticate with Twitch")


class TwitchUserNotFoundError(TwitchError):
    def __init__(self, login: str) -> None:
        super().__init__(f"Twitch user '{login}' not found")
        self.login = login


class InvalidTwitchSignatureError(TwitchError):
    """Raised when Twitch webhook signature verification fails."""

    def __init__(self) -> None:
        super().__init__("Invalid Twitch webhook signature")
