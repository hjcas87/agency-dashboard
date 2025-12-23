"""
Celery application configuration.

Celery usa RabbitMQ como broker para ejecutar tareas en background.
RabbitMQ proporciona fiabilidad, persistencia y buena gestión de colas
para garantizar que las tareas se ejecuten correctamente (retries, resultados, etc).
"""
from celery import Celery

from app.config import settings

# Configuración de Celery con RabbitMQ
celery_app = Celery(
    "core",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    result_expires=3600,  # Results expire after 1 hour
    task_send_sent_event=True,  # Enable events for monitoring
    worker_send_task_events=True,  # Enable task events
)

