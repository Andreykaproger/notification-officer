class StreamerAlreadyExistsError(Exception):
    """Raised when attempting to create a streamer with an existing login."""

    def __init__(self, login: str) -> None:
        self.login = login
        super().__init__(f"Streamer with this {login} already exists")

    pass


class StreamerNotFoundError(Exception):
    """Raised when a streamer cannot be found."""

    def __init__(self, streamer_id: int) -> None:
        self.streamer_id = streamer_id
        super().__init__(f"Streamer {streamer_id} not found")
