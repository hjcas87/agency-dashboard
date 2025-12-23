"""
Main API router that aggregates all feature routers.
"""
from fastapi import APIRouter

# Import core feature routers
from app.core.features.n8n.routes import router as n8n_router
from app.core.features.health.routes import router as health_router
from app.core.features.users.routes import router as users_router

# Import custom feature routers (if they exist)
try:
    from app.custom.features import get_custom_routers
    custom_routers = get_custom_routers()
except (ImportError, AttributeError):
    custom_routers = []

# Create main API router
api_router = APIRouter()

# Include core feature routers
api_router.include_router(n8n_router)
api_router.include_router(health_router)
api_router.include_router(users_router)

# Include custom feature routers (if they exist)
for router in custom_routers:
    api_router.include_router(router)

