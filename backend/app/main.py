"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Side-effect import: loading `app.models` is what registers every
# SQLAlchemy mapped class with `Base.metadata`. The lifespan handler
# below calls `Base.metadata.create_all()` in DEVELOPMENT, and that
# read of the metadata depends on every class having been imported —
# any model not loaded here yields a missing table at startup. F401
# suppressed because the import is intentional side effect, no name
# is referenced from `app.models` in this file.
import app.models  # noqa: F401
from app.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.core.router import api_router
from app.database import Base, engine

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

    # Serve uploaded files via dedicated endpoint
    uploads_dir = Path(__file__).parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    from fastapi import HTTPException as _HTTPException
    from fastapi import Request
    from fastapi.responses import FileResponse

    async def _serve_upload(request: Request):
        """Serve uploaded files (logos, etc.)."""
        file_path = request.path_params.get("file_path", "")
        full_path = uploads_dir / file_path
        resolved = full_path.resolve()
        if not str(resolved).startswith(str(uploads_dir.resolve())):
            raise _HTTPException(status_code=403, detail="Access denied")
        if full_path.exists() and full_path.is_file():
            return FileResponse(str(full_path))
        raise _HTTPException(status_code=404, detail=f"File not found: {full_path}")

    app.add_api_route(
        "/uploads/{file_path:path}",
        _serve_upload,
        methods=["GET"],
        tags=["uploads"],
    )

    # Include routers
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

    # Health check moved to features/health

    return app


app = create_app()
