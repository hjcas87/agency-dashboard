"""
Integration tests para health check endpoints.
"""
import pytest
from unittest.mock import patch, Mock

from app.shared.services.kafka_broker import KafkaBroker
from app.shared.services.n8n_service import N8NService


@pytest.mark.integration
class TestHealthRoutes:
    """Tests de integración para health check."""

    def test_health_check_endpoint_success(self, client):
        """Test de health check endpoint exitoso."""
        # Arrange
        with patch("app.core.features.health.routes.KafkaBroker") as mock_kafka:
            with patch("app.core.features.health.routes.N8NService") as mock_n8n:
                mock_kafka_instance = Mock()
                mock_kafka_instance.health_check.return_value = True
                mock_kafka.return_value = mock_kafka_instance

                mock_n8n_instance = Mock()
                mock_n8n_instance.health_check.return_value = True
                mock_n8n.return_value = mock_n8n_instance

                # Act
                response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert data["module"] == "core"
        assert "details" in data

    def test_health_check_endpoint_degraded(self, client):
        """Test de health check cuando algún servicio falla."""
        # Arrange
        with patch("app.core.features.health.routes.KafkaBroker") as mock_kafka:
            with patch("app.core.features.health.routes.N8NService") as mock_n8n:
                mock_kafka_instance = Mock()
                mock_kafka_instance.health_check.return_value = False  # Kafka falla
                mock_kafka.return_value = mock_kafka_instance

                mock_n8n_instance = Mock()
                mock_n8n_instance.health_check.return_value = True
                mock_n8n.return_value = mock_n8n_instance

                # Act
                response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["details"]["kafka"] is False
        assert data["details"]["n8n"] is True

