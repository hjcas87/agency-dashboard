"""
End-to-end tests para flujos completos del sistema.
Estos tests requieren que todos los servicios estén corriendo.
"""
import pytest
import time
from tests.factories.user_factory import UserFactory


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflows:
    """Tests end-to-end para flujos completos."""

    def test_user_crud_complete_workflow(self, client, db_session):
        """
        Test E2E del flujo completo CRUD de usuarios.
        """
        # 1. Crear usuario
        user_data = {
            "email": "e2e_user@example.com",
            "name": "E2E Test User",
            "is_active": True,
        }
        create_response = client.post("/api/v1/users", json=user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # 2. Obtener usuario creado
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["email"] == user_data["email"]

        # 3. Actualizar usuario
        update_data = {"name": "Updated E2E User"}
        update_response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["name"] == update_data["name"]

        # 4. Listar usuarios (debe incluir el creado)
        list_response = client.get("/api/v1/users")
        assert list_response.status_code == 200
        user_ids = [u["id"] for u in list_response.json()["items"]]
        assert user_id in user_ids

        # 5. Eliminar usuario
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # 6. Verificar que fue eliminado
        get_deleted_response = client.get(f"/api/v1/users/{user_id}")
        assert get_deleted_response.status_code == 404

    def test_health_check_workflow(self, client):
        """
        Test E2E del flujo de health check.
        """
        # Act
        response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "module" in data
        assert "details" in data
        assert "database" in data["details"]
        assert "kafka" in data["details"]
        assert "n8n" in data["details"]

    def test_n8n_workflow_trigger_flow(self, client):
        """
        Test E2E del flujo de trigger de workflow N8N.
        Nota: Requiere N8N corriendo o será mocked.
        """
        # Arrange
        workflow_data = {
            "workflow_id": "test-workflow",
            "payload": {
                "test": "e2e",
                "timestamp": time.time(),
            },
        }

        # Act
        trigger_response = client.post("/api/v1/n8n/trigger", json=workflow_data)

        # Assert
        assert trigger_response.status_code == 200
        data = trigger_response.json()
        assert "task_id" in data
        assert data["status"] == "queued"

        # Obtener estado de la tarea
        task_id = data["task_id"]
        status_response = client.get(f"/api/v1/n8n/task/{task_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "state" in status_data
        assert status_data["task_id"] == task_id

