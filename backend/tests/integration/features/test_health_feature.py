"""
Integration tests para el feature completo de Health.
Testa el flujo completo: Routes → Service → Health Checks.
"""
import pytest
from unittest.mock import patch, Mock
from sqlalchemy import text

from app.shared.services.kafka_broker import KafkaBroker
from app.shared.services.n8n_service import N8NService
from app.core.features.health.service import HealthFeatureService
from app.database import engine


@pytest.mark.integration
class TestHealthFeature:
    """Tests de integración para el feature completo de Health."""

    @pytest.fixture
    def kafka_broker(self):
        """Fixture para KafkaBroker."""
        return KafkaBroker()

    @pytest.fixture
    def n8n_service(self):
        """Fixture para N8NService."""
        return N8NService()

    @pytest.fixture
    def health_service(self, kafka_broker, n8n_service):
        """Fixture para HealthFeatureService."""
        return HealthFeatureService(kafka_broker, n8n_service)

    def test_check_health_all_healthy(self, health_service, db_session):
        """Test de health check cuando todos los servicios están saludables."""
        # Arrange
        with patch.object(health_service.kafka_broker, "health_check", return_value=True):
            with patch.object(health_service.n8n_service, "health_check", return_value=True):
                # Act
                result = health_service.check_health()

        # Assert
        assert result["status"] == "healthy"
        assert result["module"] == "core"
        assert result["details"]["database"] is True
        assert result["details"]["kafka"] is True
        assert result["details"]["n8n"] is True

    def test_check_health_degraded(self, health_service, db_session):
        """Test de health check cuando algún servicio falla."""
        # Arrange
        with patch.object(health_service.kafka_broker, "health_check", return_value=False):
            with patch.object(health_service.n8n_service, "health_check", return_value=True):
                # Act
                result = health_service.check_health()

        # Assert
        assert result["status"] == "degraded"
        assert result["details"]["kafka"] is False
        assert result["details"]["n8n"] is True

    def test_check_database_connection(self, health_service, db_session):
        """Test de verificación de conexión a base de datos."""
        # Act
        result = health_service._check_database()

        # Assert
        assert result is True

