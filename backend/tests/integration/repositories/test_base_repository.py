"""
Integration tests para BaseRepository.
"""
import pytest
from sqlalchemy import Column, Integer, String
from app.shared.repositories.base_repository import BaseRepository
from app.database import Base


# Modelo de test
class TestModel(Base):
    __tablename__ = "test_models"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    value = Column(String(100))


@pytest.mark.integration
@pytest.mark.database
class TestBaseRepository:
    """Tests de integración para BaseRepository."""

    @pytest.fixture
    def repository(self, db_session):
        """Fixture para crear repositorio de test."""
        return BaseRepository(TestModel, db_session)

    def test_create(self, repository):
        """Test de creación de registro."""
        # Arrange
        data = {"name": "test", "value": "value1"}

        # Act
        result = repository.create(data)

        # Assert
        assert result.id is not None
        assert result.name == "test"
        assert result.value == "value1"

    def test_get(self, repository):
        """Test de obtener registro por ID."""
        # Arrange
        created = repository.create({"name": "test", "value": "value1"})

        # Act
        result = repository.get(created.id)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "test"

    def test_get_not_found(self, repository):
        """Test de obtener registro inexistente."""
        # Act
        result = repository.get(99999)

        # Assert
        assert result is None

    def test_get_all(self, repository):
        """Test de obtener todos los registros."""
        # Arrange
        repository.create({"name": "test1", "value": "value1"})
        repository.create({"name": "test2", "value": "value2"})

        # Act
        results = repository.get_all()

        # Assert
        assert len(results) == 2

    def test_get_all_with_filters(self, repository):
        """Test de obtener registros con filtros."""
        # Arrange
        repository.create({"name": "test1", "value": "value1"})
        repository.create({"name": "test2", "value": "value2"})

        # Act
        results = repository.get_all(filters={"name": "test1"})

        # Assert
        assert len(results) == 1
        assert results[0].name == "test1"

    def test_update(self, repository):
        """Test de actualización de registro."""
        # Arrange
        created = repository.create({"name": "test", "value": "value1"})

        # Act
        updated = repository.update(created.id, {"value": "value2"})

        # Assert
        assert updated.value == "value2"
        assert updated.name == "test"  # No cambió

    def test_delete(self, repository):
        """Test de eliminación de registro."""
        # Arrange
        created = repository.create({"name": "test", "value": "value1"})

        # Act
        result = repository.delete(created.id)

        # Assert
        assert result is True
        assert repository.get(created.id) is None

    def test_count(self, repository):
        """Test de contar registros."""
        # Arrange
        repository.create({"name": "test1", "value": "value1"})
        repository.create({"name": "test2", "value": "value2"})

        # Act
        count = repository.count()

        # Assert
        assert count == 2

    def test_count_with_filters(self, repository):
        """Test de contar registros con filtros."""
        # Arrange
        repository.create({"name": "test1", "value": "value1"})
        repository.create({"name": "test2", "value": "value2"})

        # Act
        count = repository.count(filters={"name": "test1"})

        # Assert
        assert count == 1

