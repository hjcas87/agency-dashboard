"""
Integration tests para el feature completo de N8N.
Testa el flujo completo: Routes → Service → External Service.
"""
import pytest
from unittest.mock import patch, AsyncMock, Mock

from app.shared.services.n8n_service import N8NService
from app.core.features.n8n.service import N8NFeatureService
from app.core.tasks.celery_app import celery_app


@pytest.mark.integration
class TestN8NFeature:
    """Tests de integración para el feature completo de N8N."""

    @pytest.fixture
    def n8n_service(self):
        """Fixture para N8NService."""
        return N8NService()

    @pytest.fixture
    def n8n_feature_service(self, n8n_service):
        """Fixture para N8NFeatureService."""
        return N8NFeatureService(n8n_service)

    @pytest.mark.asyncio
    async def test_trigger_workflow_async_flow(self, n8n_feature_service):
        """Test del flujo completo de trigger asíncrono."""
        # Arrange
        workflow_id = "test-workflow"
        payload = {"key": "value"}

        # Act
        with patch("app.core.features.n8n.service.trigger_n8n_workflow") as mock_task:
            mock_task_result = Mock()
            mock_task_result.id = "test-task-id"
            mock_task.delay.return_value = mock_task_result

            result = await n8n_feature_service.trigger_workflow_async(
                workflow_id=workflow_id,
                payload=payload,
            )

        # Assert
        assert result["task_id"] == "test-task-id"
        assert result["status"] == "queued"
        mock_task.delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_workflow_sync_flow(self, n8n_feature_service, n8n_service):
        """Test del flujo completo de trigger síncrono."""
        # Arrange
        workflow_id = "test-workflow"
        payload = {"key": "value"}

        # Act
        with patch.object(n8n_service, "trigger_workflow") as mock_trigger:
            mock_trigger.return_value = {
                "status": "success",
                "status_code": 200,
                "data": {"result": "ok"},
            }

            result = await n8n_feature_service.trigger_workflow_sync(
                workflow_id=workflow_id,
                payload=payload,
            )

        # Assert
        assert result["status"] == "success"
        mock_trigger.assert_called_once_with(
            workflow_id=workflow_id,
            payload=payload,
        )

    def test_get_task_status_flow(self, n8n_feature_service):
        """Test del flujo completo de obtener estado de tarea."""
        # Arrange
        task_id = "test-task-id"

        # Act
        with patch.object(celery_app, "AsyncResult") as mock_async_result:
            mock_result = Mock()
            mock_result.state = "SUCCESS"
            mock_result.result = {"status": "completed"}
            mock_async_result.return_value = mock_result

            result = n8n_feature_service.get_task_status(task_id)

        # Assert
        assert result["task_id"] == task_id
        assert result["state"] == "SUCCESS"
        assert result["result"] == {"status": "completed"}

