"""
Integration tests para Users endpoints.
"""
import pytest
from tests.factories.user_factory import UserFactory


@pytest.mark.integration
@pytest.mark.database
class TestUsersRoutes:
    """Tests de integración para Users endpoints."""

    def test_create_user_success(self, client, db_session):
        """Test de creación de usuario exitosa."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "is_active": True,
        }

        # Act
        response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_email(self, client, db_session):
        """Test de creación de usuario con email duplicado."""
        # Arrange
        existing_user = UserFactory.create(db_session, email="existing@example.com")
        user_data = {
            "email": "existing@example.com",
            "name": "Another User",
        }

        # Act
        response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_get_user_success(self, client, db_session):
        """Test de obtener usuario exitoso."""
        # Arrange
        user = UserFactory.create(db_session)

        # Act
        response = client.get(f"/api/v1/users/{user.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email

    def test_get_user_not_found(self, client):
        """Test de obtener usuario inexistente."""
        # Act
        response = client.get("/api/v1/users/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_users_list(self, client, db_session):
        """Test de obtener lista de usuarios."""
        # Arrange
        UserFactory.create_batch(db_session, count=5)

        # Act
        response = client.get("/api/v1/users?skip=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 5

    def test_get_users_active_only(self, client, db_session):
        """Test de obtener solo usuarios activos."""
        # Arrange
        UserFactory.create(db_session, is_active=True)
        UserFactory.create(db_session, is_active=False)

        # Act
        response = client.get("/api/v1/users?active_only=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(user["is_active"] for user in data["items"])

    def test_get_users_search(self, client, db_session):
        """Test de búsqueda de usuarios."""
        # Arrange
        UserFactory.create(db_session, name="John Doe", email="john@example.com")
        UserFactory.create(db_session, name="Jane Smith", email="jane@example.com")

        # Act
        response = client.get("/api/v1/users?search=John")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("John" in user["name"] for user in data["items"])

    def test_update_user_success(self, client, db_session):
        """Test de actualización de usuario exitosa."""
        # Arrange
        user = UserFactory.create(db_session, name="Old Name")
        update_data = {"name": "New Name"}

        # Act
        response = client.put(f"/api/v1/users/{user.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["email"] == user.email  # No cambió

    def test_update_user_not_found(self, client):
        """Test de actualización de usuario inexistente."""
        # Act
        response = client.put("/api/v1/users/99999", json={"name": "New Name"})

        # Assert
        assert response.status_code == 404

    def test_delete_user_success(self, client, db_session):
        """Test de eliminación de usuario exitosa."""
        # Arrange
        user = UserFactory.create(db_session)

        # Act
        response = client.delete(f"/api/v1/users/{user.id}")

        # Assert
        assert response.status_code == 204

        # Verificar que fue eliminado
        get_response = client.get(f"/api/v1/users/{user.id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        """Test de eliminación de usuario inexistente."""
        # Act
        response = client.delete("/api/v1/users/99999")

        # Assert
        assert response.status_code == 404

