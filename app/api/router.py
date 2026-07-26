from fastapi import FastAPI

from app.api.routers import api_router


def configure_routers(app: FastAPI) -> None:
    app.include_router(api_router)
