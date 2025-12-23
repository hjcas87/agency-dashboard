# Trazabilidad de Tareas Celery

Esta guía explica cómo monitorear y obtener trazabilidad de las tareas ejecutadas por Celery.

## Opciones para Trazabilidad

### 1. Flower - Interfaz Web de Monitoreo (Recomendado)

Flower es una herramienta web para monitorear y administrar tareas Celery en tiempo real.

#### Acceso a Flower

- **Desarrollo**: http://localhost:5555
- **Producción**: https://flower.${DOMAIN} (si está configurado con Traefik)

#### Credenciales por defecto

- Usuario: `admin`
- Contraseña: `admin`

Configurar en variables de entorno:
```env
FLOWER_USER=admin
FLOWER_PASSWORD=tu-password-seguro
```

#### Características de Flower

- **Tareas en tiempo real**: Ver tareas ejecutándose, pendientes y completadas
- **Historial de tareas**: Ver todas las tareas ejecutadas con detalles
- **Estados de tareas**: PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
- **Workers**: Ver estado de los workers, carga, tareas activas
- **Estadísticas**: Métricas de rendimiento, tasas de éxito/fallo
- **Control**: Cancelar o revocar tareas
- **Gráficos**: Visualizaciones de rendimiento y carga

#### Ejemplo de uso

1. Abrir Flower en el navegador
2. Navegar a "Tasks" para ver todas las tareas
3. Hacer clic en una tarea para ver:
   - Estado actual
   - UUID de la tarea
   - Argumentos y resultados
   - Tiempo de ejecución
   - Stack trace si falló

### 2. Result Backend - Obtener Estado Programáticamente

Celery usa un result backend para almacenar los resultados de las tareas. En este proyecto usamos `rpc://` que almacena resultados en memoria del worker.

#### Obtener Estado de una Tarea

```python
from app.core.tasks.celery_app import celery_app

# Obtener resultado de una tarea
task_id = "abc-123-def-456"
task = celery_app.AsyncResult(task_id)

# Verificar estado
print(task.state)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED

# Obtener resultado si está completa
if task.state == "SUCCESS":
    result = task.result
    print(f"Resultado: {result}")
elif task.state == "FAILURE":
    error = task.info
    print(f"Error: {error}")
```

#### Ejemplo en el Feature de N8N

El feature de N8N ya tiene implementado esto:

```python
from app.core.features.n8n.service import N8NFeatureService

service = N8NFeatureService(n8n_service)

# Disparar workflow y obtener task_id
result = await service.trigger_workflow_async(
    workflow_id="my-workflow",
    payload={"data": "value"}
)
task_id = result["task_id"]

# Obtener estado después
status = service.get_task_status(task_id)
print(status)  # {"task_id": "...", "state": "SUCCESS", "result": {...}}
```

### 3. Logs de Celery Worker

Los workers de Celery generan logs detallados de todas las tareas.

#### Ver logs en Docker

```bash
# Ver logs del worker
docker-compose logs -f celery_worker

# Filtrar por tarea específica
docker-compose logs celery_worker | grep "trigger_n8n_workflow"
```

#### Configuración de Logging

El logging está configurado en `celery_app.py` con:
- `task_track_started=True`: Registra cuando una tarea comienza
- `worker_send_task_events=True`: Envía eventos para Flower
- Logs incluyen: task_id, nombre de tarea, argumentos, estado, resultado

### 4. RabbitMQ Management UI

RabbitMQ tiene una interfaz web de administración que muestra:

- **Queues**: Colas de tareas pendientes
- **Messages**: Mensajes en cola
- **Connections**: Conexiones activas
- **Channels**: Canales abiertos

#### Acceso

- **Desarrollo**: http://localhost:15672
- **Producción**: https://rabbitmq.${DOMAIN}

#### Credenciales

- Usuario: `admin` (o `RABBITMQ_USER`)
- Contraseña: `admin` (o `RABBITMQ_PASSWORD`)

### 5. Persistencia de Resultados (Opcional)

Si necesitas persistir resultados más allá de la ejecución:

#### Opción A: Redis como Result Backend

```python
# En config.py
CELERY_RESULT_BACKEND = "redis://redis:6379/0"

# Ventajas:
# - Resultados persisten después de reiniciar
# - Puedes consultar resultados históricos
```

#### Opción B: Base de Datos como Result Backend

```python
# En config.py
CELERY_RESULT_BACKEND = "db+postgresql://user:pass@localhost/celery"

# Ventajas:
# - Resultados en base de datos permanente
# - Puedes hacer queries SQL sobre resultados
# - Integración con tu esquema de datos
```

## Estados de Tareas

- **PENDING**: Tarea está esperando ser ejecutada
- **STARTED**: Tarea comenzó a ejecutarse
- **SUCCESS**: Tarea completó exitosamente
- **FAILURE**: Tarea falló
- **RETRY**: Tarea está siendo reintentada
- **REVOKED**: Tarea fue cancelada

## Mejores Prácticas

1. **Siempre guardar task_id**: Cuando disparas una tarea, guarda el `task_id` para consultar su estado después
2. **Usar Flower para desarrollo**: Es la forma más fácil de monitorear tareas durante desarrollo
3. **Implementar endpoints de estado**: Como en el feature de N8N, expone endpoints para consultar el estado de tareas
4. **Logging estructurado**: Asegúrate de que tus tareas logueen información relevante (task_id, argumentos, resultados)
5. **Result backend apropiado**: Usa `rpc://` para desarrollo, considera Redis o DB para producción si necesitas persistencia

## Ejemplo Completo

```python
from app.core.tasks.n8n_tasks import trigger_n8n_workflow
from app.core.tasks.celery_app import celery_app

# Disparar tarea
task_result = trigger_n8n_workflow.delay(
    workflow_url="http://n8n:5678/webhook/my-workflow",
    payload={"key": "value"}
)

task_id = task_result.id
print(f"Tarea creada: {task_id}")

# Monitorear estado (en otro lugar o después)
task = celery_app.AsyncResult(task_id)

# Polling para estado
import time
while task.state == "PENDING":
    print(f"Esperando... estado: {task.state}")
    time.sleep(1)
    task = celery_app.AsyncResult(task_id)

# Resultado final
if task.state == "SUCCESS":
    print(f"Resultado: {task.result}")
elif task.state == "FAILURE":
    print(f"Error: {task.info}")
```

## Recursos Adicionales

- [Documentación de Celery - Monitoring](https://docs.celeryq.dev/en/stable/userguide/monitoring.html)
- [Flower GitHub](https://github.com/mher/flower)
- [RabbitMQ Management](https://www.rabbitmq.com/management.html)

