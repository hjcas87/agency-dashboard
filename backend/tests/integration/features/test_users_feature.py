"""
Integration tests para el feature completo de Users.
"""
import pytest
from sqlalchemy.orm import Session

from app.core.features.users.repository import UserRepository
from app.core.features.users.service import UserService
from app.core.features.users.schemas import UserCreate, UserUpdate
from tests.factories.user_factory import UserFactory


@pytest.mark.integration
@pytest.mark.database
class TestUsersFeature:
    """Tests de integración para el feature completo de Users."""

    @pytest.fixture
    def user_repository(self, db_session: Session):
        """Fixture para UserRepository."""
        return UserRepository(db_session)

    @pytest.fixture
    def user_service(self, user_repository: UserRepository):
        """Fixture para UserService."""
        return UserService(user_repository)

    def test_create_user_flow(self, user_service, db_session):
        """Test del flujo completo de creación de usuario."""
        # Arrange
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            is_active=True,
        )

        # Act
        user = user_service.create_user(user_data)

        # Assert
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active is True

    def test_create_user_duplicate_email(self, user_service, db_session):
        """Test de creación con email duplicado."""
        # Arrange
        UserFactory.create(db_session, email="duplicate@example.com")
        user_data = UserCreate(
            email="duplicate@example.com",
            name="Another User",
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            user_service.create_user(user_data)
        assert "already exists" in str(exc_info.value).lower()

    def test_get_user_flow(self, user_service, db_session):
        """Test del flujo completo de obtener usuario."""
        # Arrange
        user = UserFactory.create(db_session)

        # Act
        result = user_service.get_user(user.id)

        # Assert
        assert result.id == user.id
        assert result.email == user.email

    def test_get_users_with_filters(self, user_service, db_session):
        """Test de obtener usuarios con filtros."""
        # Arrange
        UserFactory.create(db_session, is_active=True)
        UserFactory.create(db_session, is_active=False)
        UserFactory.create(db_session, is_active=True)

        # Act
        active_users, total = user_service.get_users(active_only=True)

        # Assert
        assert len(active_users) == 2
        assert all(user.is_active for user in active_users)

    def test_update_user_flow(self, user_service, db_session):
        """Test del flujo completo de actualización."""
        # Arrange
        user = UserFactory.create(db_session, name="Old Name")
        update_data = UserUpdate(name="New Name")

        # Act
        updated = user_service.update_user(user.id, update_data)

        # Assert
        assert updated.name == "New Name"
        assert updated.email == user.email  # No cambió

    def test_delete_user_flow(self, user_service, db_session):
        """Test del flujo completo de eliminación."""
        # Arrange
        user = UserFactory.create(db_session)

        # Act
        result = user_service.delete_user(user.id)

        # Assert
        assert result is True

        # Verificar que fue eliminado
        with pytest.raises(Exception) as exc_info:
            user_service.get_user(user.id)
        assert "not found" in str(exc_info.value).lower()

