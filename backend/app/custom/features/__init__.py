"""
Custom features module.
Each feature should be self-contained with its own structure.
"""
from fastapi import APIRouter


def get_custom_routers() -> list[APIRouter]:
    """
    Return list of custom feature routers.
    Register new feature routers here as they are created.
    """
    from app.custom.features.clients.routes import router as clients_router

    routers = [
        clients_router,
    ]

    return routers
