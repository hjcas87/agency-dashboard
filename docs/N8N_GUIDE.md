# Guía de N8N

## Introducción

N8N es una plataforma de automatización de workflows que permite crear flujos de trabajo complejos sin código.

## Configuración

N8N está configurado para:
- Usar PostgreSQL como base de datos
- Autenticación básica (configurable)
- Almacenar workflows en volumen Docker

## Acceso

- **Desarrollo**: http://localhost:5678
- **Producción**: https://n8n.{DOMAIN}

Credenciales por defecto (cambiar en producción):
- Usuario: `admin`
- Contraseña: `admin`

## Crear un Workflow

### 1. Crear Webhook Trigger

1. En N8N, crear un nuevo workflow
2. Agregar nodo "Webhook"
3. Configurar:
   - Method: POST
   - Path: `/webhook/my-workflow`
   - Response Mode: "When Last Node Finishes"

### 2. Agregar Nodos

Ejemplos de nodos útiles:
- **HTTP Request**: Llamar APIs externas
- **Code**: Ejecutar JavaScript/Python
- **IF**: Lógica condicional
- **Set**: Transformar datos
- **PostgreSQL**: Consultar base de datos

### 3. Activar Workflow

1. Guardar el workflow
2. Activar el toggle "Active"
3. Copiar la URL del webhook

## Integración con Backend

### Disparar desde FastAPI

```python
from app.core.tasks import trigger_n8n_workflow

# Disparar de forma asíncrona
task = trigger_n8n_workflow.delay(
    workflow_url="http://n8n:5678/webhook/my-workflow",
    payload={
        "user_id": 123,
        "action": "process",
        "data": {...}
    }
)

# Obtener resultado
result = task.get(timeout=30)
```

### Endpoint REST

```bash
POST /api/v1/n8n/trigger
{
  "workflow_url": "http://n8n:5678/webhook/my-workflow",
  "payload": {
    "key": "value"
  }
}
```

### Verificar Estado de Tarea

```bash
GET /api/v1/n8n/task/{task_id}
```

## Ejemplos de Workflows

### 1. Procesar Datos y Enviar Email

```
Webhook → Transform Data → Send Email → Respond
```

### 2. Integración con IA

```
Webhook → OpenAI API → Process Response → Save to DB → Respond
```

### 3. Webhook Chain

```
Webhook → Validate → Call External API → Transform → Call Another API → Respond
```

## Mejores Prácticas

1. **Nombres descriptivos**: Usa nombres claros para workflows y nodos
2. **Error handling**: Agrega nodos de error handling
3. **Logging**: Usa nodos de logging para debugging
4. **Testing**: Prueba workflows con datos de ejemplo
5. **Documentación**: Documenta workflows complejos
6. **Versionado**: Exporta workflows importantes a `automation/workflows/`

## Exportar/Importar Workflows

### Exportar

1. En N8N, abrir el workflow
2. Click en "..." → "Download"
3. Guardar en `automation/workflows/`

### Importar

1. En N8N, click en "Workflows" → "Import from File"
2. Seleccionar archivo JSON del workflow

## Monitoreo

N8N incluye métricas que se pueden monitorear:
- Workflows activos
- Ejecuciones exitosas/fallidas
- Tiempo de ejecución

## Troubleshooting

### Workflow no se dispara

1. Verificar que el workflow esté activo
2. Verificar la URL del webhook
3. Revisar logs de N8N: `docker-compose logs n8n`

### Error de conexión a DB

1. Verificar variables de entorno de N8N
2. Verificar que PostgreSQL esté corriendo
3. Verificar credenciales de DB

### Timeout en workflows largos

1. Aumentar timeout en configuración de N8N
2. Dividir workflow en múltiples workflows más pequeños
3. Usar ejecución asíncrona

## Recursos

- [Documentación oficial de N8N](https://docs.n8n.io/)
- [Nodos disponibles](https://docs.n8n.io/integrations/)
- [Ejemplos de workflows](https://n8n.io/workflows/)

