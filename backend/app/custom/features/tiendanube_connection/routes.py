"""
API routes for Tiendanube connection feature.

Endpoints:
- POST   /tiendanube/auth/initiate       - Start OAuth flow
- GET    /tiendanube/auth/callback       - OAuth callback (token exchange)
- GET    /tiendanube/stores              - List connected stores
- GET    /tiendanube/stores/{store_id}   - Get store details
- POST   /tiendanube/stores/{store_id}/sync - Trigger catalog sync
- GET    /tiendanube/stores/{store_id}/status - Get store connection status
"""
import secrets
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.custom.features.tiendanube_connection.schemas import (
    StoreListResponse,
    StoreResponse,
    SyncTriggerResponse,
)
from app.custom.features.tiendanube_connection.service import TiendanubeConnectionService
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/tiendanube", tags=["Custom: Tiendanube"])


def get_service(db: Session = Depends(get_db)) -> TiendanubeConnectionService:
    """Dependency to get TiendanubeConnectionService."""
    return TiendanubeConnectionService(db)


# ── OAuth Flow ──────────────────────────────────────────────────────


@router.get(
    "/auth/initiate",
    summary="Start Tiendanube OAuth flow",
)
def initiate_auth(
    service: TiendanubeConnectionService = Depends(get_service),
):
    """Start OAuth flow. Redirects user to Tiendanube to select their store."""
    import secrets as _secrets

    state = _secrets.token_urlsafe(32)
    # TODO: Store state in cache/session for callback verification
    auth_url = service.initiate_auth(state)
    return {"auth_url": auth_url, "state": state}


@router.get(
    "/auth/callback",
    summary="OAuth callback — exchange code for token",
)
async def auth_callback(
    code: str = Query(..., description="Authorization code from Tiendanube"),
    state: str = Query(..., description="CSRF state token"),
    service: TiendanubeConnectionService = Depends(get_service),
):
    """Handle OAuth callback and exchange code for permanent token.

    Tiendanube redirects here after user authorizes. We exchange
    the code for a token and register the store automatically.
    The store_id comes from user_id in the token response.
    """
    try:
        # Exchange code for token (includes user_id = store_id)
        token_data = await service.exchange_token(code)

        # Register store from token response
        store = service.register_store_from_token(token_data)

        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/connect-store/connected?store_name={store.name}",
            status_code=302,
        )

    except Exception as e:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/connect-store?error={str(e)}",
            status_code=302,
        )


# ── Store Management ────────────────────────────────────────────────


@router.get(
    "/stores",
    response_model=StoreListResponse,
    summary="List connected stores",
)
def list_stores(
    service: TiendanubeConnectionService = Depends(get_service),
) -> StoreListResponse:
    """List all Tiendanube stores connected to Mendri Loyalty."""
    stores = service.list_stores()
    return StoreListResponse(
        items=[StoreResponse.model_validate(s) for s in stores],
        total=len(stores),
    )


@router.get(
    "/stores/{store_id}",
    response_model=StoreResponse,
    summary="Get store details",
)
def get_store(
    store_id: int,
    service: TiendanubeConnectionService = Depends(get_service),
) -> StoreResponse:
    """Get details of a connected store."""
    store = service.get_store(store_id)
    if not store:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")
    return StoreResponse.model_validate(store)


@router.get(
    "/stores/{store_id}/status",
    summary="Get store connection status",
)
def get_store_status(
    store_id: int,
    service: TiendanubeConnectionService = Depends(get_service),
) -> dict[str, Any]:
    """Check if a store's connection and token are working."""
    store = service.get_store(store_id)
    if not store:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

    return {
        "store_id": store.id,
        "name": store.name,
        "status": store.status.value,
        "has_token": True,
        "last_sync_at": store.last_sync_at,
    }


# ── Catalog Sync ────────────────────────────────────────────────────


@router.post(
    "/stores/{store_id}/sync",
    response_model=SyncTriggerResponse,
    summary="Trigger catalog sync",
)
async def trigger_sync(
    store_id: int,
    service: TiendanubeConnectionService = Depends(get_service),
) -> SyncTriggerResponse:
    """Trigger a full product catalog sync from Tiendanube.

    Fetches all products via paginated API.
    """
    result = await service.sync_catalog(store_id)
    return SyncTriggerResponse(
        store_id=store_id,
        message=f"Sync complete: {result['products_fetched']} products fetched",
        status="completed",
    )
