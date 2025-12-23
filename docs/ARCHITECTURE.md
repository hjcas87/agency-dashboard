# Arquitectura del Sistema

## Visión General

El sistema está diseñado con una **arquitectura modular por features**, siguiendo principios de Clean Architecture y Domain-Driven Design.

> **¿Por qué Features y no Modules?** Ver [Decisiones Arquitectónicas](./ARCHITECTURE_DECISIONS.md) para una comparación detallada.

## Estructura del Backend

```
backend/app/
├── core/                    # Módulos base (NO modificar en forks)
│   ├── features/            # Features core autocontenidos
│   │   ├── n8n/            # Feature de N8N
│   │   │   ├── routes.py   # Endpoints
│   │   │   ├── schemas.py  # DTOs
│   │   │   ├── service.py  # Lógica de negocio
│   │   │   └── README.md
│   │   └── health/         # Feature de health check
│   ├── config.py           # Configuración
│   ├── database.py         # DB setup
│   ├── router.py           # Router principal
│   └── tasks/              # Tareas Celery
├── custom/                  # Módulos personalizados (modificar aquí)
│   └── features/           # Features custom
└── shared/                 # Código compartido
    ├── interfaces/         # Interfaces y contratos
    ├── services/           # Servicios compartidos
    └── repositories/       # Repositorios base
```

## Arquitectura por Features

Cada feature es autocontenido y sigue esta estructura:

```
feature_name/
├── routes.py       # Endpoints FastAPI (capa de presentación)
├── schemas.py      # DTOs y validación (Pydantic)
├── service.py      # Lógica de negocio (capa de aplicación)
├── repository.py  # Acceso a datos (capa de dominio, opcional)
├── models.py       # Modelos de dominio (SQLAlchemy, opcional)
└── README.md       # Documentación
```

### Flujo de Request

```
Request → Routes → Service → Repository → Database
                ↓
            External Services (N8N, etc.)
                ↓
            Message Broker (Kafka)
```

## Capas de la Arquitectura

### 1. Routes (Presentación)
- Maneja HTTP requests/responses
- Valida entrada con Pydantic schemas
- Dependency injection de servicios

### 2. Service (Aplicación)
- Contiene lógica de negocio
- Orquesta llamadas a repositorios y servicios externos
- Maneja transacciones

### 3. Repository (Dominio)
- Abstrae acceso a datos
- Implementa patrón Repository
- Hereda de `BaseRepository` para operaciones comunes

### 4. Models (Dominio)
- Modelos SQLAlchemy
- Representan entidades del dominio

## Servicios Compartidos

### Interfaces

Definen contratos para servicios:

- `IMessageBroker` - Para message brokers (Kafka, RabbitMQ, etc.)
- `IExternalService` - Para servicios externos (N8N, APIs, etc.)

### Implementaciones

- `KafkaBroker` - Implementación de Kafka
- `N8NService` - Wrapper para N8N

### Repositorios

- `BaseRepository` - Repositorio genérico con CRUD básico

## Message Broker: Kafka

Kafka se usa para:
- Mensajería asíncrona robusta
- Background tasks con Celery
- Event-driven architecture

### Ventajas sobre Redis

- **Persistencia**: Mensajes persisten en disco
- **Escalabilidad**: Mejor para sistemas distribuidos
- **Throughput**: Mayor capacidad de procesamiento
- **Replicación**: Replicación nativa de mensajes

## Patrones de Diseño

### Dependency Injection
FastAPI dependencies para inyectar servicios:

```python
def get_service() -> MyService:
    return MyService()

@router.get("/endpoint")
async def endpoint(service: MyService = Depends(get_service)):
    return service.do_something()
```

### Repository Pattern
Abstrae acceso a datos:

```python
class UserRepository(BaseRepository[User]):
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(self.model).filter(
            self.model.email == email
        ).first()
```

### Service Layer
Separa lógica de negocio:

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_data: dict) -> User:
        # Validaciones, transformaciones, etc.
        return self.user_repo.create(user_data)
```

### Wrapper Pattern
Envuelve servicios externos:

```python
class N8NService(IExternalService):
    async def call(self, endpoint: str, ...):
        # Implementación específica de N8N
```

## Extensión

### Agregar un Feature Custom

1. Crear estructura en `app/custom/features/my_feature/`
2. Implementar routes, schemas, service
3. Registrar router en `app/custom/features/__init__.py`

### Agregar un Servicio Compartido

1. Definir interface en `app/shared/interfaces/`
2. Implementar en `app/shared/services/`
3. Usar dependency injection en features

## Escalabilidad

### Horizontal Scaling
- FastAPI con múltiples workers
- Celery workers escalables
- Kafka con múltiples particiones

### Caching
- Implementar caching en services cuando sea necesario
- Usar Redis para cache (opcional, separado del message broker)

### Database
- Connection pooling con SQLAlchemy
- Migraciones con Alembic
- Índices apropiados

## Testing

Estructura recomendada:

```
tests/
├── core/
│   └── features/
│       ├── test_n8n_routes.py
│       └── test_n8n_service.py
├── custom/
└── conftest.py
```

Usar fixtures para:
- Database sessions
- Test client
- Mock de servicios externos

