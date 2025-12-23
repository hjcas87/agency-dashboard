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
    
    # Ejemplo: importar routers de features custom
    # try:
    #     from app.custom.features.example_feature.routes import router as example_router
    #     routers.append(example_router)
    # except ImportError:
    #     pass
    
    return routers

