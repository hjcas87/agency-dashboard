"""
Unit tests for health check service.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.core.features.health.service import HealthFeatureService


@pytest.mark.unit
class TestHealthFeatureService:
    """Tests for HealthFeatureService."""

    def test_check_health_all_healthy(self):
        """Health check returns healthy when all services are up."""
        # Arrange
        n8n_service = MagicMock()
        n8n_service.health_check.return_value = True

        service = HealthFeatureService(n8n_service=n8n_service)

        with patch.object(service, "_check_database", return_value=True), \
             patch.object(service, "_check_rabbitmq", return_value=True):
            # Act
            result = service.check_health()

            # Assert
            assert result["status"] == "healthy"
            assert result["module"] == "core"
            assert result["details"]["database"] is True
            assert result["details"]["rabbitmq"] is True
            assert result["details"]["n8n"] is True

    def test_check_health_degraded_when_service_down(self):
        """Health check returns degraded when any service is down."""
        # Arrange
        n8n_service = MagicMock()
        n8n_service.health_check.return_value = False

        service = HealthFeatureService(n8n_service=n8n_service)

        with patch.object(service, "_check_database", return_value=True), \
             patch.object(service, "_check_rabbitmq", return_value=True):
            # Act
            result = service.check_health()

            # Assert
            assert result["status"] == "degraded"
            assert result["details"]["n8n"] is False
