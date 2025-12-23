# Arquitectura del Backend

## Visión General

El backend está construido con FastAPI siguiendo una arquitectura modular que separa código core (actualizable) de código custom (específico del cliente).

## Estructura

```
backend/
├── app/
│   ├── core/              # Módulos base (NO modificar)
│   │   ├── api/           # Endpoints core
│   │   ├── config.py      # Configuración
│   │   ├── database.py    # Configuración DB
│   │   ├── router.py      # Router principal
│   │   ├── schemas.py     # Schemas Pydantic
│   │   └── tasks/         # Tareas Celery
│   ├── custom/            # Módulos personalizados (modificar aquí)
│   │   └── api/           # Endpoints custom
│   └── shared/            # Utilidades compartidas
├── alembic/               # Migraciones de DB
└── requirements.txt       # Dependencias
```

## Flujo de Request

```
Request → FastAPI App → Router → Core/Custom API → Service → Database
                                              ↓
                                         Celery Task → N8N
```

## Componentes Principales

### 1. Configuración (`app/core/config.py`)

Usa Pydantic Settings para manejar variables de entorno de forma type-safe.

### 2. Base de Datos (`app/core/database.py`)

- SQLAlchemy ORM
- Session management con dependency injection
- Alembic para migraciones

### 3. Routers

- `app/core/router.py`: Agrega todos los routers
- `app/core/api/router.py`: Endpoints core
- `app/custom/api/router.py`: Endpoints custom (opcional)

### 4. Tareas Celery

Las tareas asíncronas se ejecutan en background workers:

- `celery_worker`: Ejecuta tareas
- `celery_beat`: Ejecuta tareas programadas

### 5. Integración con N8N

Los workflows de N8N se disparan mediante tareas Celery:

```python
from app.core.tasks import trigger_n8n_workflow

task = trigger_n8n_workflow.delay(
    workflow_url="http://n8n:5678/webhook/id",
    payload={"data": "value"}
)
```

## Patrones de Diseño

### Dependency Injection

FastAPI usa dependency injection para:
- Database sessions
- Authentication
- Configuración

### Repository Pattern (Opcional)

Para lógica compleja, considera usar el patrón Repository:

```python
# app/custom/repositories/user_repository.py
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
```

### Service Layer

Separa lógica de negocio de los endpoints:

```python
# app/custom/services/user_service.py
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_data: dict):
        # Lógica de negocio aquí
        return self.user_repo.create(user_data)
```

## Escalabilidad

### Horizontal Scaling

- FastAPI con múltiples workers (Gunicorn/Uvicorn)
- Celery workers escalables
- PostgreSQL con connection pooling

### Caching

Considera Redis para:
- Cache de queries frecuentes
- Session storage
- Rate limiting

### Background Tasks

Usa Celery para:
- Tareas largas
- Integraciones externas (N8N)
- Procesamiento asíncrono

## Seguridad

### Autenticación

Implementa JWT tokens:

```python
from app.core.auth import get_current_user

@router.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user": user}
```

### Validación

Pydantic valida automáticamente:
- Request bodies
- Query parameters
- Path parameters

### CORS

Configurado en `app/main.py` con CORS middleware.

## Testing

Estructura recomendada:

```
backend/
├── tests/
│   ├── core/
│   ├── custom/
│   └── conftest.py
```

Usa pytest con fixtures para:
- Database sessions
- Test client
- Mock de servicios externos

