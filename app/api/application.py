from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.lifespan import lifespan
from app.api.router import configure_routers
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    configure_routers(app)
    register_exception_handlers(app)

    return app
