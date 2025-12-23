# N8N Feature

Feature autocontenido para manejo de workflows de N8N.

## Estructura

```
n8n/
├── routes.py      # Endpoints FastAPI
├── schemas.py     # Schemas Pydantic
├── service.py     # Lógica de negocio
└── README.md      # Esta documentación
```

## Endpoints

- `POST /api/v1/n8n/trigger` - Dispara un workflow de forma asíncrona
- `GET /api/v1/n8n/task/{task_id}` - Obtiene el estado de una tarea

## Uso

```python
# Desde otro feature o servicio
from app.shared.services.n8n_service import N8NService
from app.core.features.n8n.service import N8NFeatureService

n8n_service = N8NService()
feature_service = N8NFeatureService(n8n_service)

# Disparar workflow
result = await feature_service.trigger_workflow_async(
    workflow_id="my-workflow-id",
    payload={"key": "value"}
)
```

## Dependencias

- `N8NService` (wrapper para N8N)
- `Celery` (para ejecución asíncrona)

