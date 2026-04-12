"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.core.router import api_router
from app.core.logging_config import setup_logging, get_logger

# Import all models to ensure SQLAlchemy can resolve relationships
# This must be imported before Base.metadata.create_all()
import app.models  # noqa: F401

# Setup logging with Rich
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("[bold cyan]Starting up application...[/bold cyan]")
    if settings.ENVIRONMENT == "DEVELOPMENT":
        logger.debug("Creating database tables (development mode)")
        Base.metadata.create_all(bind=engine)
    logger.info("[bold green]✓[/bold green] Application started successfully")
    yield
    # Shutdown
    logger.info("[bold yellow]Shutting down application...[/bold yellow]")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    logger.info(f"[bold blue]Creating FastAPI app:[/bold blue] {settings.PROJECT_NAME}")
    
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
        # Custom feature tags — add here as features are created:
        # {"name": "Custom: <Feature>", "description": "Descripción del feature (custom)."},
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

