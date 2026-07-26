from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.exceptions.streamer import (
    StreamerAlreadyExistsError,
    StreamerNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(StreamerNotFoundError)
    async def streamer_not_found_handler(request: Request, exc: StreamerNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(StreamerAlreadyExistsError)
    async def streamer_already_exists_handler(
        request: Request, exc: StreamerAlreadyExistsError
    ):
        return JSONResponse(status_code=409, content={"detail": str(exc)})
