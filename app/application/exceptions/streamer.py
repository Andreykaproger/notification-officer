class StreamerAlreadyExistsError(Exception):
    """Raised when attempting to create a streamer with an existing login."""

    pass


class StreamerNotFoundError(Exception):
    """Raised when a streamer cannot be found."""

    def __init__(self, streamer_id: int) -> None:
        self.streamer_id = streamer_id
        super().__init__(f"Streamer {streamer_id} not found")
