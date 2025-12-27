"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.core.router import api_router

# Import all models to ensure SQLAlchemy can resolve relationships
# This must be imported before Base.metadata.create_all()
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    if settings.ENVIRONMENT == "DEVELOPMENT":
        Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (if needed in the future)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Tags metadata para organizar la documentación de Swagger
    tags_metadata = [
        {
            "name": "Core: Auth",
            "description": "Endpoints de autenticación y autorización (core).",
        },
        {
            "name": "Core: Users",
            "description": "Gestión de usuarios (core).",
        },
        {
            "name": "Core: N8N",
            "description": "Integración con N8N para workflows (core).",
        },
        {
            "name": "Core: Health",
            "description": "Health checks y estado del sistema (core).",
        },
        {
            "name": "Custom: Campaigns",
            "description": "Gestión de campañas de publicidad (custom).",
        },
        {
            "name": "Custom: Contacts",
            "description": "Gestión de contactos (custom).",
        },
        {
            "name": "Custom: Journeys",
            "description": "Gestión de customer journeys (custom).",
        },
        {
            "name": "Custom: Opportunities",
            "description": "Gestión de oportunidades de venta (custom).",
        },
        {
            "name": "Custom: Activities",
            "description": "Gestión de actividades (custom).",
        },
        {
            "name": "Custom: Integrations",
            "description": "Gestión de integraciones (custom).",
        },
        {
            "name": "Custom: Pipelines",
            "description": "Gestión de pipelines de ventas (custom).",
        },
        {
            "name": "Custom: Automations",
            "description": "Gestión de automatizaciones (custom).",
        },
    ]
    
    app = FastAPI(
        title="Core API",
        description="Boilerplate API with modular architecture",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        openapi_tags=tags_metadata,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

    # Health check moved to features/health

    return app


app = create_app()

