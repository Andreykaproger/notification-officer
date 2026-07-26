from fastapi import APIRouter

from .health import health_router
from .streamers import streamers_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(streamers_router, tags=["Streamers"])
