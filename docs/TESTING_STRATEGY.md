# Estrategia de Testing

## Filosofía

Seguimos **Test-Driven Development (TDD)** y principios de testing escalable:

1. **Tests como documentación**: Los tests documentan el comportamiento esperado
2. **Fast feedback**: Tests rápidos para desarrollo ágil
3. **Confianza**: Tests que dan confianza para refactorizar
4. **Coverage**: > 80% de cobertura de código
5. **Pirámide de testing**: Más unit tests, menos integration, pocos E2E

## Pirámide de Testing

```
        /\
       /E2E\        ← Pocos tests end-to-end
      /------\
     /Integration\  ← Tests de integración moderados
    /------------\
   /   Unit Tests  \ ← Muchos tests unitarios rápidos
  /----------------\
```

### Distribución Recomendada

- **70% Unit Tests**: Rápidos, sin dependencias externas
- **25% Integration Tests**: Base de datos, servicios mockeados
- **5% E2E Tests**: Flujos completos con todos los servicios

## Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidas
├── unit/                    # Tests unitarios
│   ├── services/           # Tests de servicios
│   ├── repositories/        # Tests de repositorios
│   └── utils/              # Tests de utilidades
├── integration/            # Tests de integración
│   ├── api/                # Tests de endpoints
│   ├── features/           # Tests de features completos
│   ├── repositories/       # Tests de repos con DB
│   └── external/           # Tests de servicios externos
└── e2e/                    # Tests end-to-end (opcional)
    └── workflows/          # Flujos completos
```

## Tipos de Tests

### Unit Tests

**Características**:
- Testan una unidad de código (función, método, clase)
- Sin dependencias externas (todo mockeado)
- Muy rápidos (< 100ms)
- Determinísticos

**Ejemplo**:
```python
@pytest.mark.unit
def test_n8n_service_trigger_workflow():
    service = N8NService()
    with patch('httpx.AsyncClient') as mock_client:
        # Test implementation
        pass
```

### Integration Tests

**Características**:
- Testan múltiples componentes trabajando juntos
- Usan base de datos real (test DB)
- Servicios externos mockeados
- Rápidos (< 1s)

**Ejemplo**:
```python
@pytest.mark.integration
def test_n8n_endpoint_trigger_workflow(client):
    response = client.post("/api/v1/n8n/trigger", json={...})
    assert response.status_code == 200
```

### E2E Tests

**Características**:
- Testan flujos completos del sistema
- Requieren todos los servicios (Docker Compose)
- Lentos (> 1s)
- Pocos pero críticos

**Ejemplo**:
```python
@pytest.mark.e2e
def test_complete_workflow_flow():
    # Test completo desde request hasta resultado
    pass
```

## Mejores Prácticas

### 1. AAA Pattern (Arrange, Act, Assert)

```python
def test_example():
    # Arrange - Preparar datos
    service = MyService()
    input_data = {"key": "value"}
    
    # Act - Ejecutar acción
    result = service.process(input_data)
    
    # Assert - Verificar resultado
    assert result["status"] == "success"
```

### 2. Naming Conventions

```python
# Formato: test_<what>_<condition>_<expected_result>
def test_n8n_service_trigger_workflow_success():
    pass

def test_n8n_service_trigger_workflow_invalid_id_raises_error():
    pass
```

### 3. Fixtures

```python
@pytest.fixture
def db_session():
    # Setup
    session = create_session()
    yield session
    # Teardown
    session.close()
```

### 4. Mocks y Patches

```python
# Mock de servicios externos
with patch('httpx.AsyncClient') as mock_client:
    mock_client.return_value.json.return_value = {"result": "ok"}
    result = await service.call_external_api()
```

### 5. Parametrización

```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("invalid", False),
])
def test_validation(input, expected):
    assert validate(input) == expected
```

### 6. Test Isolation

- Cada test debe ser independiente
- No compartir estado entre tests
- Usar fixtures para setup/teardown

### 7. Test Data

- Usar factories para crear datos de test
- No depender de datos de producción
- Limpiar datos después de cada test

## Cobertura de Tests

### Objetivo: > 80%

```bash
# Ver cobertura
pytest --cov=app --cov-report=html

# Abrir reporte
open htmlcov/index.html
```

### Qué Testear

✅ **Sí testear**:
- Lógica de negocio
- Servicios
- Repositorios
- Endpoints
- Validaciones
- Transformaciones de datos

❌ **No testear**:
- Código de frameworks (FastAPI, SQLAlchemy)
- Librerías externas
- Código generado automáticamente

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo unit tests
pytest -m unit

# Solo integration tests
pytest -m integration

# Tests específicos
pytest tests/unit/services/test_n8n_service.py

# Con coverage
pytest --cov=app --cov-report=html

# Verbose
pytest -v

# Con output
pytest -s

# Parallelo (si tienes pytest-xdist)
pytest -n auto
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Debugging Tests

```python
# Usar pdb para debugging
import pdb; pdb.set_trace()

# O usar pytest --pdb para entrar en debugger en fallos
pytest --pdb
```

## Test Data Management

```python
# Factories para crear datos de test
@pytest.fixture
def user_factory(db_session):
    def _create_user(**kwargs):
        defaults = {"name": "Test User", "email": "test@example.com"}
        defaults.update(kwargs)
        return UserRepository(User, db_session).create(defaults)
    return _create_user
```

## Performance Testing

```python
@pytest.mark.slow
def test_performance():
    import time
    start = time.time()
    # ... código a testear
    elapsed = time.time() - start
    assert elapsed < 1.0  # Debe completarse en menos de 1 segundo
```

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

