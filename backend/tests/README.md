# Testing Strategy

## Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidas
├── unit/                    # Tests unitarios (rápidos, sin dependencias externas)
│   ├── services/
│   ├── repositories/
│   └── utils/
├── integration/            # Tests de integración
│   ├── api/                # Tests de endpoints
│   ├── database/           # Tests de base de datos
│   └── external/           # Tests de servicios externos (mocked)
└── e2e/                    # Tests end-to-end (opcional)
```

## Tipos de Tests

### Unit Tests
- **Scope**: Funciones, métodos, clases individuales
- **Dependencias**: Mockeadas
- **Velocidad**: Muy rápidos (< 100ms)
- **Ejemplo**: `tests/unit/services/test_n8n_service.py`

### Integration Tests
- **Scope**: Múltiples componentes trabajando juntos
- **Dependencias**: Base de datos real (test DB), servicios mockeados
- **Velocidad**: Rápidos (< 1s)
- **Ejemplo**: `tests/integration/api/test_n8n_routes.py`

### E2E Tests
- **Scope**: Flujos completos del sistema
- **Dependencias**: Todos los servicios (Docker Compose)
- **Velocidad**: Lentos (> 1s)
- **Ejemplo**: `tests/e2e/test_workflow_complete.py`

## Marcadores de Pytest

- `@pytest.mark.unit` - Tests unitarios
- `@pytest.mark.integration` - Tests de integración
- `@pytest.mark.slow` - Tests lentos
- `@pytest.mark.external` - Requieren servicios externos
- `@pytest.mark.kafka` - Requieren Kafka
- `@pytest.mark.n8n` - Requieren N8N
- `@pytest.mark.database` - Requieren base de datos

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo unit tests
pytest -m unit

# Solo integration tests
pytest -m integration

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/services/test_n8n_service.py

# Verbose
pytest -v

# Con output de prints
pytest -s
```

## Mejores Prácticas

1. **AAA Pattern**: Arrange, Act, Assert
2. **Fixtures**: Reutilizar setup común
3. **Mocks**: Mockear servicios externos
4. **Isolation**: Cada test debe ser independiente
5. **Naming**: `test_<what>_<condition>_<expected_result>`
6. **Coverage**: Mantener > 80% de cobertura
7. **Fast**: Tests unitarios deben ser muy rápidos
8. **Deterministic**: Tests deben ser determinísticos

## Ejemplo de Test

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_n8n_service_trigger_workflow_success():
    # Arrange
    service = N8NService()
    workflow_id = "test-workflow"
    payload = {"key": "value"}
    
    # Act
    with patch.object(service, 'call') as mock_call:
        mock_call.return_value = {"status": "success"}
        result = await service.trigger_workflow(workflow_id, payload)
    
    # Assert
    assert result["status"] == "success"
    mock_call.assert_called_once()
```

