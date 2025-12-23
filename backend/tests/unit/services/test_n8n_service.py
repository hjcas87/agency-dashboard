"""
Unit tests para N8NService.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.shared.services.n8n_service import N8NService


@pytest.mark.unit
class TestN8NService:
    """Tests unitarios para N8NService."""

    @pytest.fixture
    def n8n_service(self):
        """Fixture para crear instancia de N8NService."""
        return N8NService()

    @pytest.mark.asyncio
    async def test_call_success(self, n8n_service):
        """Test de llamada exitosa a N8N."""
        # Arrange
        endpoint = "/webhook/test"
        payload = {"key": "value"}
        expected_response = {
            "status": "success",
            "status_code": 200,
            "data": {"result": "ok"},
        }

        # Act
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "ok"}
            mock_response.content = b'{"result": "ok"}'
            mock_response.raise_for_status = Mock()

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            result = await n8n_service.call(
                endpoint=endpoint,
                method="POST",
                payload=payload,
            )

        # Assert
        assert result["status"] == "success"
        assert result["status_code"] == 200
        assert result["data"] == {"result": "ok"}

    @pytest.mark.asyncio
    async def test_call_http_error(self, n8n_service):
        """Test de manejo de error HTTP."""
        # Arrange
        endpoint = "/webhook/test"
        payload = {"key": "value"}

        # Act & Assert
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = Exception("HTTP 500")

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            with pytest.raises(Exception):
                await n8n_service.call(
                    endpoint=endpoint,
                    method="POST",
                    payload=payload,
                )

    @pytest.mark.asyncio
    async def test_trigger_workflow_success(self, n8n_service):
        """Test de trigger de workflow exitoso."""
        # Arrange
        workflow_id = "test-workflow"
        payload = {"data": "test"}

        # Act
        with patch.object(n8n_service, "call") as mock_call:
            mock_call.return_value = {
                "status": "success",
                "status_code": 200,
                "data": {"workflow_id": workflow_id},
            }

            result = await n8n_service.trigger_workflow(
                workflow_id=workflow_id,
                payload=payload,
            )

        # Assert
        assert result["status"] == "success"
        mock_call.assert_called_once_with(
            endpoint=f"/webhook/{workflow_id}",
            method="POST",
            payload=payload,
        )

    def test_health_check_success(self, n8n_service):
        """Test de health check exitoso."""
        # Arrange & Act
        with patch.object(n8n_service, "call") as mock_call:
            mock_call.return_value = {"status": "success"}
            result = n8n_service.health_check()

        # Assert
        assert result is True

    def test_health_check_failure(self, n8n_service):
        """Test de health check fallido."""
        # Arrange & Act
        with patch.object(n8n_service, "call", side_effect=Exception("Connection error")):
            result = n8n_service.health_check()

        # Assert
        assert result is False

