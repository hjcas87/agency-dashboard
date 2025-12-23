"""
Performance tests para operaciones de usuarios.
"""
import pytest
import time
from tests.factories.user_factory import UserFactory


@pytest.mark.performance
@pytest.mark.slow
class TestUserPerformance:
    """Tests de rendimiento para operaciones de usuarios."""

    def test_create_user_performance(self, client, db_session):
        """Test de rendimiento de creación de usuarios."""
        # Arrange
        user_data = {
            "email": "perf_test@example.com",
            "name": "Performance Test User",
        }

        # Act
        start_time = time.time()
        response = client.post("/api/v1/users", json=user_data)
        elapsed_time = time.time() - start_time

        # Assert
        assert response.status_code == 201
        assert elapsed_time < 0.5  # Debe completarse en menos de 500ms

    def test_get_users_list_performance(self, client, db_session):
        """Test de rendimiento de listado de usuarios."""
        # Arrange
        UserFactory.create_batch(db_session, count=100)

        # Act
        start_time = time.time()
        response = client.get("/api/v1/users?skip=0&limit=100")
        elapsed_time = time.time() - start_time

        # Assert
        assert response.status_code == 200
        assert elapsed_time < 1.0  # Debe completarse en menos de 1 segundo

    def test_search_users_performance(self, client, db_session):
        """Test de rendimiento de búsqueda de usuarios."""
        # Arrange
        UserFactory.create_batch(db_session, count=50)
        UserFactory.create(db_session, name="Search Target User")

        # Act
        start_time = time.time()
        response = client.get("/api/v1/users?search=Search Target")
        elapsed_time = time.time() - start_time

        # Assert
        assert response.status_code == 200
        assert elapsed_time < 0.5  # Debe completarse en menos de 500ms

    def test_batch_create_performance(self, client, db_session):
        """Test de rendimiento de creación en batch."""
        # Arrange
        users_to_create = 20

        # Act
        start_time = time.time()
        for i in range(users_to_create):
            user_data = {
                "email": f"batch_{i}@example.com",
                "name": f"Batch User {i}",
            }
            response = client.post("/api/v1/users", json=user_data)
            assert response.status_code == 201
        elapsed_time = time.time() - start_time

        # Assert
        avg_time_per_user = elapsed_time / users_to_create
        assert avg_time_per_user < 0.3  # Promedio de menos de 300ms por usuario

