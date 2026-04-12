"""
Service layer for Tiendanube connection feature.

Handles:
- OAuth flow (initiate, callback, token exchange)
- Store registration and management
- Token encryption/decryption
- Catalog sync from Tiendanube API
"""
import logging
from datetime import datetime
from typing import Any

import httpx
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.config import settings
from app.custom.features.tiendanube_connection.models import Store, StoreStatus, TiendanubeToken
from app.custom.features.tiendanube_connection.schemas import (
    TiendanubeStoreInfo,
    TiendanubeTokenResponse,
)

logger = logging.getLogger(__name__)

# Tiendanube OAuth endpoints
TIENDANUBE_AUTH_URL = "https://www.tiendanube.com/apps/{client_id}/authorize"
TIENDANUBE_TOKEN_URL = "https://www.tiendanube.com/apps/authorize/token"
TIENDANUBE_API_BASE = "https://api.tiendanube.com/v1"

# Required OAuth scopes for Mendri Loyalty
REQUIRED_SCOPES = [
    "read_products",
    "write_products",
    "read_orders",
    "write_orders",
    "read_customers",
    "write_customers",
]


def _get_fernet() -> Fernet:
    """Get Fernet instance for token encryption.

    Uses SECRET_KEY from settings with a fixed suffix for deterministic
    key derivation in development. In production, use a proper FERNET_KEY.
    """
    key_source = getattr(settings, "FERNET_KEY", None) or f"{settings.SECRET_KEY}-tiendanube"
    # Pad or truncate to 32 bytes for Fernet
    key_bytes = key_source.encode()[:32].ljust(32, b"\0")
    import base64
    b64_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(b64_key)


class TiendanubeConnectionService:
    """Service for managing Tiendanube store connections."""

    def __init__(self, db: Session):
        self.db = db
        self._fernet = _get_fernet()

    # ── OAuth Flow ──────────────────────────────────────────────────

    def initiate_auth(self, state: str) -> str:
        """Generate the authorization URL for Tiendanube OAuth flow.

        No store_id needed — Tiendanube will prompt the user to select
        their store after logging in.

        Args:
            state: CSRF state token.

        Returns:
            Full authorization URL.

        Raises:
            ValueError: If TIENDANUBE_CLIENT_ID is not configured.
        """
        scopes = ",".join(REQUIRED_SCOPES)
        client_id = settings.TIENDANUBE_CLIENT_ID
        if not client_id:
            raise ValueError("TIENDANUBE_CLIENT_ID is not configured")
        return (
            f"{TIENDANUBE_AUTH_URL.format(client_id=client_id)}"
            f"?response_type=code"
            f"&scope={scopes}"
            f"&state={state}"
        )

    async def exchange_token(
        self,
        code: str,
    ) -> TiendanubeTokenResponse:
        """Exchange authorization code for permanent access token.

        Uses client credentials from app settings.

        Args:
            code: Authorization code from Tiendanube redirect.

        Returns:
            Parsed token response from Tiendanube.

        Raises:
            ValueError: If token exchange fails.
        """
        payload = {
            "client_id": settings.TIENDANUBE_CLIENT_ID,
            "client_secret": settings.TIENDANUBE_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                TIENDANUBE_TOKEN_URL,
                json=payload,
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.error(
                    "Tiendanube token exchange failed: %s — %s",
                    response.status_code,
                    response.text,
                )
                raise ValueError(
                    f"Token exchange failed: {response.status_code} — {response.text}"
                )

            return TiendanubeTokenResponse(**response.json())

    # ── Store Management ────────────────────────────────────────────

    def register_store_from_token(self, token_data: TiendanubeTokenResponse) -> Store:
        """Register or update a store from token exchange response.

        The user_id from the token response IS the store_id.
        We create a placeholder name since we don't fetch store info
        in this simplified flow.

        Args:
            token_data: Token response from Tiendanube (includes user_id).

        Returns:
            The created or updated Store model.
        """
        store_id_str = str(token_data.user_id)

        # Find or create store
        store = (
            self.db.query(Store)
            .filter(Store.tiendanube_store_id == store_id_str)
            .first()
        )

        if store:
            store.status = StoreStatus.ACTIVE
            store.is_active = True
            logger.info("Updated existing store: %s", store.name)
        else:
            store = Store(
                name=f"Tienda {store_id_str}",
                tiendanube_store_id=store_id_str,
                status=StoreStatus.ACTIVE,
                is_active=True,
            )
            self.db.add(store)
            logger.info("Registered new store: %s", store.name)

        self.db.flush()

        # Store encrypted token
        self._save_token(store.id, token_data)

        self.db.commit()
        self.db.refresh(store)
        return store

    def register_store(
        self,
        token_data: TiendanubeTokenResponse,
        store_info: TiendanubeStoreInfo,
    ) -> Store:
        """Register or update a store after successful OAuth token exchange.

        Args:
            token_data: Token response from Tiendanube.
            store_info: Store metadata from Tiendanube API.

        Returns:
            The created or updated Store model.
        """
        store_id_str = str(token_data.user_id)

        # Find or create store
        store = (
            self.db.query(Store)
            .filter(Store.tiendanube_store_id == store_id_str)
            .first()
        )

        if store:
            store.name = store_info.name
            store.domain = store_info.domain or store.domain
            store.currency = store_info.currency
            store.status = StoreStatus.ACTIVE
            store.is_active = True
            logger.info("Updated existing store: %s", store.name)
        else:
            store = Store(
                name=store_info.name,
                tiendanube_store_id=store_id_str,
                domain=store_info.domain,
                currency=store_info.currency,
                status=StoreStatus.ACTIVE,
                is_active=True,
            )
            self.db.add(store)
            logger.info("Registered new store: %s", store.name)

        self.db.flush()

        # Store encrypted token
        self._save_token(store.id, token_data)

        self.db.commit()
        self.db.refresh(store)
        return store

    def _save_token(self, store_id: int, token_data: TiendanubeTokenResponse) -> None:
        """Encrypt and store the access token.

        Args:
            store_id: The store's database ID.
            token_data: Token response from Tiendanube.
        """
        encrypted = self._fernet.encrypt(token_data.access_token.encode())

        existing = (
            self.db.query(TiendanubeToken)
            .filter(TiendanubeToken.store_id == store_id)
            .first()
        )

        if existing:
            existing.encrypted_access_token = encrypted.decode()
            existing.token_type = token_data.token_type
            existing.scope = token_data.scope
        else:
            token_record = TiendanubeToken(
                store_id=store_id,
                encrypted_access_token=encrypted.decode(),
                token_type=token_data.token_type,
                scope=token_data.scope,
            )
            self.db.add(token_record)

    def get_access_token(self, store_id: int) -> str:
        """Decrypt and return the access token for a store.

        Args:
            store_id: The store's database ID.

        Returns:
            Decrypted access token string.

        Raises:
            ValueError: If no token found for store.
        """
        token_record = (
            self.db.query(TiendanubeToken)
            .filter(TiendanubeToken.store_id == store_id)
            .first()
        )

        if not token_record:
            raise ValueError(f"No token found for store {store_id}")

        return self._fernet.decrypt(token_record.encrypted_access_token.encode()).decode()

    def get_store(self, store_id: int) -> Store | None:
        """Get a store by its database ID.

        Args:
            store_id: The store's database ID.

        Returns:
            Store model or None.
        """
        return (
            self.db.query(Store)
            .filter(Store.id == store_id)
            .first()
        )

    def list_stores(self) -> list[Store]:
        """List all connected stores.

        Returns:
            List of Store models.
        """
        return (
            self.db.query(Store)
            .filter(Store.is_active == True)
            .order_by(Store.created_at.desc())
            .all()
        )

    # ── Tiendanube API Client ───────────────────────────────────────

    async def tiendanube_request(
        self,
        store_id: int,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        """Make an authenticated request to the Tiendanube API.

        Args:
            store_id: The store's database ID.
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API path (e.g., '/products', '/orders').
            params: Query parameters.
            json_body: JSON request body.

        Returns:
            Parsed JSON response.

        Raises:
            ValueError: If store or token not found.
            httpx.HTTPStatusError: If API returns an error.
        """
        store = self.get_store(store_id)
        if not store:
            raise ValueError(f"Store {store_id} not found")

        access_token = self.get_access_token(store_id)

        url = f"{TIENDANUBE_API_BASE}/{store.tiendanube_store_id}{path}"
        headers = {
            "Authentication": f"bearer {access_token}",
            "User-Agent": "mendri-loyalty",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    # ── Catalog Sync ────────────────────────────────────────────────

    async def sync_catalog(self, store_id: int) -> dict[str, int]:
        """Sync product catalog from Tiendanube.

        Fetches all products via paginated API and upserts into local DB.

        Args:
            store_id: The store's database ID.

        Returns:
            Dict with sync stats: products_fetched, products_created, products_updated.
        """
        store = self.get_store(store_id)
        if not store:
            raise ValueError(f"Store {store_id} not found")

        store.status = StoreStatus.SYNCING
        self.db.commit()

        total_fetched = 0

        try:
            # Fetch all products (paginated)
            page = 1
            while True:
                products = await self.tiendanube_request(
                    store_id,
                    "GET",
                    "/products",
                    params={"per_page": 100, "page": page},
                )

                if not products:
                    break

                total_fetched += len(products)
                page += 1

                # TODO: Upsert products into local DB
                # This will be implemented when we have Product models
                logger.info(
                    "Fetched %d products (page %d) for store %s",
                    len(products),
                    page - 1,
                    store.name,
                )

            store.status = StoreStatus.ACTIVE
            store.last_sync_at = datetime.now()
            self.db.commit()

            logger.info(
                "Catalog sync complete for store %s: %d products fetched",
                store.name,
                total_fetched,
            )

            return {
                "products_fetched": total_fetched,
                "products_created": 0,
                "products_updated": 0,
            }

        except Exception as e:
            store.status = StoreStatus.ERROR
            self.db.commit()
            logger.error("Catalog sync failed for store %s: %s", store.name, e)
            raise
