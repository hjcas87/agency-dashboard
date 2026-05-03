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
    from app.custom.features.activities.routes import router as activities_router
    from app.custom.features.clients.routes import router as clients_router
    from app.custom.features.dashboard.routes import router as dashboard_router
    from app.custom.features.email.routes import router as email_router
    from app.custom.features.invoices.routes import router as invoices_router
    from app.custom.features.pdf.routes import router as pdf_router
    from app.custom.features.proposals.routes import router as proposals_router

    routers = [
        activities_router,
        clients_router,
        proposals_router,
        invoices_router,
        pdf_router,
        email_router,
        dashboard_router,
    ]

    return routers
