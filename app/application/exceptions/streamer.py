class StreamerAlreadyExistsError(Exception):
    """Raised when attempting to create a streamer with an existing login."""

    def __init__(self, login: str) -> None:
        self.login = login
        super().__init__(f"Streamer with this {login} already exists")

    pass


class StreamerNotFoundError(Exception):
    """Raised when a streamer cannot be found."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
