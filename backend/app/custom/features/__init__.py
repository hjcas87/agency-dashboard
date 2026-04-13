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
    routers = []

    # Example:
    # from app.custom.features.my_feature.routes import router as my_feature_router
    # routers.append(my_feature_router)

    return routers
