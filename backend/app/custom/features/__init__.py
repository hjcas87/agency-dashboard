"""
Custom features module.
Cada feature debe ser autocontenido con su propia estructura.
"""
from typing import List
from fastapi import APIRouter


def get_custom_routers() -> List[APIRouter]:
    """
    Retorna lista de routers de features custom.
    Cada feature custom debe registrar su router aquí.
    """
    routers = []

    # Tiendanube Connection — OAuth, store management, catalog sync
    from app.custom.features.tiendanube_connection.routes import (
        router as tiendanube_router,
    )
    routers.append(tiendanube_router)

    return routers

