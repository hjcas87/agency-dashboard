# N8N Automation

Este directorio contiene la configuración y workflows de N8N.

## Estructura

```
automation/
├── workflows/     # Workflows de N8N exportados
└── README.md      # Esta documentación
```

## Configuración

N8N está configurado para usar PostgreSQL como base de datos y está disponible en:
- Desarrollo: http://localhost:5678
- Producción: https://n8n.{DOMAIN}

## Crear Workflows

1. Acceder a la interfaz de N8N
2. Crear un nuevo workflow
3. Configurar el webhook trigger
4. Exportar el workflow y guardarlo en `workflows/`

## Integración con Backend

El backend puede disparar workflows de N8N mediante:

```python
from app.core.tasks import trigger_n8n_workflow

# Disparar workflow de forma asíncrona
task = trigger_n8n_workflow.delay(
    workflow_url="http://n8n:5678/webhook/your-workflow-id",
    payload={"key": "value"}
)
```

## Webhooks

Los webhooks de N8N están disponibles en:
- `http://n8n:5678/webhook/{workflow-id}` (interno)
- `https://n8n.{DOMAIN}/webhook/{workflow-id}` (externo)

