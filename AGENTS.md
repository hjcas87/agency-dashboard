# Instrucciones para Agentes de IA (Codex, Cursor)

Este archivo proporciona instrucciones específicas para agentes de IA (Codex y Cursor) que trabajan en este proyecto.

> **Nota**: Cursor también lee `.cursorrules` en la raíz del proyecto. Este archivo complementa esas reglas con contexto adicional.

## Estructura del Proyecto

- **Código fuente Backend**: `backend/app/`
- **Código fuente Frontend**: `frontend/app/`
- **Tests**: `backend/tests/`
- **Documentación**: `docs/`
- **Documentación de Negocio**: `docs/business/` (requisitos, diagramas, diseños)

## Comandos de Prueba

```bash
# Ejecutar tests
cd backend && uv run pytest

# Solo unit tests
uv run pytest -m unit

# Solo integration tests
uv run pytest -m integration

# Con coverage
uv run pytest --cov=app --cov-report=html
```

## Prácticas Recomendadas

- Escribir documentación para cada función pública
- Seguir convenciones de código (ver `.cursorrules`)
- Mantener cobertura de tests > 80%
- Usar type hints siempre
- Documentar decisiones arquitectónicas

## Documentación de Negocio

**IMPORTANTE**: Antes de implementar funcionalidades, SIEMPRE consultar:

1. **`docs/business/requirements/`** - Requisitos funcionales, user stories, casos de uso
2. **`docs/business/diagrams/`** - Diagramas de flujo, arquitectura, secuencia, ER
3. **`docs/business/designs/`** - Diseños de UI/UX (Figma, mockups, wireframes)
4. **`docs/business/specs/`** - Especificaciones técnicas de negocio, APIs, modelos

### Cómo Usar la Documentación de Negocio

- **Diagramas (PNG, SVG)**:

  - Referenciar diagramas al implementar flujos de negocio
  - Leer descripciones en archivos `.md` asociados
  - Seguir flujos especificados en los diagramas

- **Diseños Figma/PDFs/Imágenes**:

  - Seguir componentes, estilos y layouts especificados
  - Consultar archivos `.md` que describen los diseños
  - Implementar UI según mockups y wireframes

- **Requisitos (Markdown)**:

  - Verificar que la implementación cumple todos los requisitos
  - Seguir user stories y casos de uso
  - Implementar reglas de negocio especificadas

- **Especificaciones**:
  - Implementar APIs según especificaciones
  - Seguir modelos de datos definidos
  - Cumplir reglas de negocio documentadas

### Proceso de Implementación

Cuando implementes una feature, SIEMPRE seguir este proceso:

1. **Revisar documentación de negocio** en `docs/business/`

   - Leer requisitos funcionales
   - Consultar diagramas relevantes
   - Revisar diseños UI/UX
   - Leer especificaciones técnicas

2. **Entender el contexto completo**

   - Flujos de negocio
   - Reglas de negocio
   - Validaciones requeridas
   - Integraciones necesarias

3. **Implementar según especificaciones**

   - Seguir diseños proporcionados
   - Implementar flujos según diagramas
   - Cumplir todos los requisitos
   - Aplicar reglas de negocio

4. **Validar implementación**

   - Verificar que cumple requisitos
   - Comparar con diseños
   - Validar flujos de negocio
   - Ejecutar tests

5. **Documentar decisiones**
   - Si hay desviaciones, documentarlas
   - Explicar decisiones técnicas
   - Actualizar documentación si es necesario

### Referenciar en Código

Siempre incluir referencias a documentación de negocio en el código:

```python
# Implementación según:
# - Requisitos: docs/business/requirements/checkout.md
# - Flujo: docs/business/diagrams/flowcharts/checkout-flow.png
# - Diseño: docs/business/designs/figma/checkout-design.md
# - Especificación: docs/business/specs/api-specs/checkout-api.md
def process_checkout(order_data: OrderCreate) -> Order:
    # ...
```

## Arquitectura

- **Backend**: FastAPI con arquitectura por features
- **Frontend**: Next.js 14+ con shadcn/ui
- **Features**: Autocontenidos en `core/features/` o `custom/features/`
- **Nunca modificar `core/`** - Solo `custom/`

## Estructura de Features

Cada feature debe tener:

- `routes.py` - Endpoints
- `schemas.py` - DTOs
- `service.py` - Lógica de negocio
- `repository.py` - Acceso a datos (opcional)
- `models.py` - Modelos (opcional)
- `README.md` - Documentación

## Gestión de Dependencias

- Usar `uv` para instalar dependencias
- Configuración en `pyproject.toml`
- Generar `uv.lock` para builds determinísticos

## Referencias Importantes

- `.cursorrules` - Reglas detalladas del proyecto (Cursor)
- `docs/ARCHITECTURE.md` - Arquitectura completa
- `docs/business/` - Documentación de negocio
- `docs/business/BEST_PRACTICES.md` - Mejores prácticas para documentación de negocio

## Contexto Adicional del Proyecto

### Propósito del Proyecto

Boilerplate reutilizable para Forward Deployed Engineers que permite:

- Desarrollo rápido de proyectos personalizados
- Extensión sin romper actualizaciones del fork original
- Arquitectura escalable y mantenible

### Stack Tecnológico

**Frontend**: Next.js 14+ (App Router), shadcn/ui, Tailwind CSS, TypeScript  
**Backend**: FastAPI, SQLAlchemy 2.0, Alembic, Python 3.11+, uv  
**Infrastructure**: Kafka, Celery, N8N, PostgreSQL, Docker Compose

### Principios de Diseño

1. **Modularidad**: Features autocontenidos
2. **Extensibilidad**: Core/Custom separation
3. **Testabilidad**: TDD, > 80% coverage
4. **Escalabilidad**: Horizontal scaling ready
5. **Mantenibilidad**: Código limpio y documentado (en ingles)

### Flujos Comunes

**Agregar un Nuevo Feature:**

1. Crear estructura en `custom/features/my_feature/`
2. Implementar: routes, schemas, service, repository (opcional), models (opcional)
3. Registrar router en `custom/features/__init__.py`
4. Agregar tests (unit + integration)
5. Documentar en README del feature (en ingles)

**Modificar Funcionalidad Existente:**

1. Verificar si está en `core/` (NO modificar)
2. Si está en `core/`, crear override en `custom/`
3. Si está en `custom/`, modificar directamente
4. Actualizar tests
5. Verificar que no rompe otros features

**Integrar Servicio Externo:**

1. Crear interface en `shared/interfaces/`
2. Implementar wrapper en `shared/services/`
3. Usar dependency injection en features
4. Mockear en tests
5. Documentar uso (en ingles)

### Ejemplos de Código

**Estructura de Feature Típica:**

```python
# routes.py
@router.post("", response_model=MyFeatureResponse)
async def create_item(
    data: MyFeatureCreate,
    service: MyFeatureService = Depends(get_my_feature_service),
):
    return service.create(data)

# service.py
class MyFeatureService:
    def __init__(self, repo: MyFeatureRepository):
        self.repo = repo

    def create(self, data: MyFeatureCreate) -> MyFeature:
        # Business logic
        return self.repo.create(data.model_dump())
```

### Convenciones Importantes

- **Naming**: snake_case (Python), camelCase (TypeScript)
- **Imports**: Ordenados con isort
- **Formatting**: Black (Python), Prettier (TypeScript)
- **Type Hints**: Siempre en Python. Usar tipos built-in de Python 3.11+:
  - `list[T]` en lugar de `List[T]` (NO importar de typing)
  - `dict[K, V]` en lugar de `Dict[K, V]` (NO importar de typing)
  - `tuple[T, ...]` en lugar de `Tuple[T, ...]` (NO importar de typing)
  - `T | None` en lugar de `Optional[T]` (NO importar Optional de typing)
  - Solo importar de `typing` cuando sea necesario (ej: `Any`, `Callable`, `TypeVar`, `Generic`)
- **Docstrings**: Google style para funciones públicas (en ingles, no incluir input y output si estan tipados)
- **Comments**: Siempre en ingles y solo cuando es necesario
