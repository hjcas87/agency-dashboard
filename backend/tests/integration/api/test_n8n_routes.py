"""
Integration tests para N8N endpoints.
"""
import pytest
from unittest.mock import patch, AsyncMock, Mock

from app.core.tasks.celery_app import celery_app


@pytest.mark.integration
class TestN8NRoutes:
    """Tests de integración para N8N endpoints."""

    def test_trigger_workflow_endpoint_success(self, client):
        """Test de trigger workflow endpoint exitoso."""
        # Arrange
        payload = {
            "workflow_id": "test-workflow",
            "payload": {"key": "value"},
        }

        # Act
        with patch("app.core.tasks.n8n_tasks.trigger_n8n_workflow") as mock_task:
            mock_task_result = Mock()
            mock_task_result.id = "test-task-id"
            mock_task.delay.return_value = mock_task_result

            response = client.post("/api/v1/n8n/trigger", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "queued"
        mock_task.delay.assert_called_once()

    def test_get_task_status_pending(self, client):
        """Test de obtener estado de tarea pendiente."""
        # Arrange
        task_id = "test-task-id"

        # Act
        with patch.object(celery_app, "AsyncResult") as mock_async_result:
            mock_result = Mock()
            mock_result.state = "PENDING"
            mock_async_result.return_value = mock_result

            response = client.get(f"/api/v1/n8n/task/{task_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["state"] == "PENDING"

    def test_get_task_status_success(self, client):
        """Test de obtener estado de tarea exitosa."""
        # Arrange
        task_id = "test-task-id"
        task_result = {"status": "success", "data": "result"}

        # Act
        with patch.object(celery_app, "AsyncResult") as mock_async_result:
            mock_result = Mock()
            mock_result.state = "SUCCESS"
            mock_result.result = task_result
            mock_async_result.return_value = mock_result

            response = client.get(f"/api/v1/n8n/task/{task_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["state"] == "SUCCESS"
        assert data["result"] == task_result

    def test_get_task_status_failure(self, client):
        """Test de obtener estado de tarea fallida."""
        # Arrange
        task_id = "test-task-id"
        error_message = "Task failed"

        # Act
        with patch.object(celery_app, "AsyncResult") as mock_async_result:
            mock_result = Mock()
            mock_result.state = "FAILURE"
            mock_result.info = error_message
            mock_async_result.return_value = mock_result

            response = client.get(f"/api/v1/n8n/task/{task_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["state"] == "FAILURE"
        assert data["error"] == error_message

