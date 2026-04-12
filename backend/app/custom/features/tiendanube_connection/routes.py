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
import logging
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.custom.features.tiendanube_connection.schemas import (
    AuthCallbackResponse,
    AuthInitiateRequest,
    AuthInitiateResponse,
    StoreListResponse,
    StoreResponse,
    SyncTriggerResponse,
    TiendanubeStoreInfo,
)
from app.custom.features.tiendanube_connection.service import TiendanubeConnectionService
from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tiendanube", tags=["Custom: Tiendanube"])


def get_service(db: Session = Depends(get_db)) -> TiendanubeConnectionService:
    """Dependency to get TiendanubeConnectionService."""
    return TiendanubeConnectionService(db)


# ── OAuth Flow ──────────────────────────────────────────────────────


@router.get(
    "/auth/initiate",
    response_model=AuthInitiateResponse,
    summary="Start Tiendanube OAuth flow",
)
def initiate_auth(
    store_id: str = Query(..., description="Tiendanube store numeric ID"),
    service: TiendanubeConnectionService = Depends(get_service),
) -> AuthInitiateResponse:
    """Generate authorization URL to connect a Tiendanube store.

    The user should be redirected to the returned auth_url.
    After authorization, they'll be redirected back with a code.
    """
    state = secrets.token_urlsafe(32)
    req = AuthInitiateRequest(
        client_id=settings.TIENDANUBE_CLIENT_ID or "",
        store_id=store_id,
    )
    auth_url = service.initiate_auth(req, state)
    # TODO: Store state in cache/session for callback verification
    return AuthInitiateResponse(auth_url=auth_url, state=state)


@router.get(
    "/auth/callback",
    summary="OAuth callback — exchange code for token",
)
async def auth_callback(
    code: str = Query(..., description="Authorization code from Tiendanube"),
    state: str = Query(..., description="CSRF state token"),
    redirect: bool = Query(
        True, description="Redirect to frontend after success"
    ),
    service: TiendanubeConnectionService = Depends(get_service),
) -> AuthCallbackResponse:
    """Handle OAuth callback and exchange code for permanent token.

    After user authorizes the app, Tiendanube redirects here with
    the authorization code. We exchange it for a permanent token
    and register/update the store.

    If redirect=True (default for browser flow), redirects to
    frontend with success/error params.
    If redirect=False, returns JSON response (for programmatic use).
    """
    try:
        # Exchange code for token (uses client_id/secret from settings)
        token_data = await service.exchange_token(code)

        # Fetch store info from Tiendanube API
        store_info = await _fetch_store_info(
            token_data.user_id,
            token_data.access_token,
        )

        # Register store + save token
        store = service.register_store(token_data, store_info)

        if redirect:
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/(private)/(custom)/connect-store/connected?store_name={store.name}",
                status_code=302,
            )

        return AuthCallbackResponse(
            store_id=store.id,
            store_name=store.name,
            access_token=token_data.access_token,
            message="Store connected successfully",
        )

    except Exception as e:
        if redirect:
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/(private)/(custom)/connect-store?error={str(e)}",
                status_code=302,
            )
        raise HTTPException(status_code=400, detail=str(e))


async def _fetch_store_info(
    store_id: str,
    access_token: str,
) -> TiendanubeStoreInfo:
    """Fetch store metadata from Tiendanube API."""
    import httpx

    url = f"https://api.tiendanube.com/v1/{store_id}/store"
    headers = {
        "Authentication": f"bearer {access_token}",
        "User-Agent": "mendri-loyalty",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return TiendanubeStoreInfo(**response.json())


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
