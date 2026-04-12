"""
Pydantic schemas for Tiendanube connection feature.
"""
from datetime import datetime

from pydantic import BaseModel, Field


# ── OAuth / Auth Flow ──────────────────────────────────────────────


class AuthInitiateRequest(BaseModel):
    """Request to initiate Tiendanube OAuth flow."""

    client_id: str = Field(..., description="Tiendanube app Client ID")
    store_id: str = Field(..., description="Tiendanube store numeric ID")


class AuthInitiateResponse(BaseModel):
    """Response with authorization URL."""

    auth_url: str = Field(..., description="URL to redirect user for authorization")
    state: str = Field(..., description="CSRF state token")


class AuthCallbackRequest(BaseModel):
    """Request body for token exchange (code → access_token)."""

    code: str = Field(..., description="Authorization code from redirect")
    client_id: str = Field(..., description="Tiendanube app Client ID")
    client_secret: str = Field(..., description="Tiendanube app Client Secret")
    state: str = Field(..., description="CSRF state token (must match initiate)")


class AuthCallbackResponse(BaseModel):
    """Response after successful token exchange."""

    store_id: int
    store_name: str
    access_token: str  # returned only once, never stored
    message: str = "Store connected successfully"


# ── Store ──────────────────────────────────────────────────────────


class StoreResponse(BaseModel):
    """Public store information (no tokens)."""

    id: int
    name: str
    tiendanube_store_id: str
    domain: str | None
    currency: str | None
    status: str
    last_sync_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    """List of connected stores."""

    items: list[StoreResponse]
    total: int


# ── Sync ───────────────────────────────────────────────────────────


class SyncTriggerResponse(BaseModel):
    """Response when catalog sync is triggered."""

    message: str = "Catalog sync started"
    store_id: int
    status: str = "syncing"


# ── Tiendanube API response schemas (for validation) ───────────────


class TiendanubeTokenResponse(BaseModel):
    """Response from Tiendanube token endpoint."""

    access_token: str
    token_type: str
    scope: str
    user_id: str


class TiendanubeStoreInfo(BaseModel):
    """Response from Tiendanube GET /store endpoint."""

    id: int
    name: str
    email: str
    domain: str | None = None
    currency: str
    logo: str | None = None
    languages: list[str] = []
