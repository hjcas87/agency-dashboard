"""
Unit tests for TiendanubeConnectionService.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.custom.features.tiendanube_connection.models import Store, StoreStatus
from app.custom.features.tiendanube_connection.schemas import (
    AuthInitiateRequest,
    TiendanubeStoreInfo,
    TiendanubeTokenResponse,
)
from app.custom.features.tiendanube_connection.service import (
    TiendanubeConnectionService,
    REQUIRED_SCOPES,
)


@pytest.mark.unit
class TestTiendanubeConnectionService:
    """Tests for TiendanubeConnectionService."""

    def test_initiate_auth_generates_url(self, db_session):
        """Auth initiation generates correct authorization URL with scopes."""
        # Arrange
        service = TiendanubeConnectionService(db_session)
        req = AuthInitiateRequest(
            client_id="test-app-123",
            store_id="456",
        )
        state = "test-state-token"
        expected_scopes = ",".join(REQUIRED_SCOPES)

        # Act
        auth_url = service.initiate_auth(req, state)

        # Assert
        assert "tiendanube.com/apps/test-app-123/authorize" in auth_url
        assert "store_id=456" in auth_url
        assert "response_type=code" in auth_url
        assert f"scope={expected_scopes}" in auth_url
        assert f"state={state}" in auth_url

    def test_register_store_creates_new_store(self, db_session):
        """Registering a new store creates both Store and TiendanubeToken records."""
        # Arrange
        service = TiendanubeConnectionService(db_session)
        token_data = TiendanubeTokenResponse(
            access_token="test-token-abc",
            token_type="bearer",
            scope="read_products,write_products",
            user_id="789",
        )
        store_info = TiendanubeStoreInfo(
            id=789,
            name="Test Store",
            email="test@store.com",
            domain="teststore.mytiendanube.com",
            currency="ARS",
        )

        # Act
        store = service.register_store(token_data, store_info)

        # Assert
        assert store.name == "Test Store"
        assert store.tiendanube_store_id == "789"
        assert store.status == StoreStatus.ACTIVE
        assert store.currency == "ARS"
        assert store.is_active is True

        # Token should be stored (encrypted)
        decrypted = service.get_access_token(store.id)
        assert decrypted == "test-token-abc"

    def test_register_store_updates_existing(self, db_session):
        """Registering an existing store updates its info instead of creating duplicate."""
        # Arrange
        service = TiendanubeConnectionService(db_session)
        token_data = TiendanubeTokenResponse(
            access_token="test-token-abc",
            token_type="bearer",
            scope="read_products",
            user_id="789",
        )
        store_info_1 = TiendanubeStoreInfo(
            id=789, name="Old Name", email="test@store.com", currency="ARS"
        )
        service.register_store(token_data, store_info_1)

        # Act: Register again with different name
        token_data_2 = TiendanubeTokenResponse(
            access_token="new-token-xyz",
            token_type="bearer",
            scope="read_products,write_products",
            user_id="789",
        )
        store_info_2 = TiendanubeStoreInfo(
            id=789, name="New Name", email="test@store.com", currency="USD"
        )
        updated_store = service.register_store(token_data_2, store_info_2)

        # Assert
        assert updated_store.name == "New Name"
        assert updated_store.currency == "USD"

        # Token should be updated
        decrypted = service.get_access_token(updated_store.id)
        assert decrypted == "new-token-xyz"

    def test_list_stores_returns_active(self, db_session):
        """List stores returns only active stores."""
        # Arrange
        service = TiendanubeConnectionService(db_session)
        token_data = TiendanubeTokenResponse(
            access_token="token1",
            token_type="bearer",
            scope="read_products",
            user_id="100",
        )
        service.register_store(
            token_data,
            TiendanubeStoreInfo(id=100, name="Store A", email="a@x.com", currency="ARS"),
        )

        # Act
        stores = service.list_stores()

        # Assert
        assert len(stores) >= 1
        assert any(s.name == "Store A" for s in stores)

    def test_get_access_token_raises_if_missing(self, db_session):
        """Getting access token for non-existent store raises ValueError."""
        # Arrange
        service = TiendanubeConnectionService(db_session)

        # Act / Assert
        with pytest.raises(ValueError, match="No token found"):
            service.get_access_token(99999)
