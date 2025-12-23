"""
Schemas para el feature de N8N.
"""
from pydantic import BaseModel
from typing import Any, Dict, Optional


class N8NTriggerRequest(BaseModel):
    """
    Request para disparar un workflow de N8N.
    
    webhook_path: Path del webhook configurado en el nodo Webhook de N8N.
                  Este es el "Path" que configuraste en el nodo Webhook, NO necesariamente
                  el workflow ID. Puede incluir paths personalizados como "webhook-test/path".
                  Ejemplo: "my-webhook", "webhook-test/348b0e40-cbbc-4146-97ad-e21d7b145ea9", 
                  o "348b0e40-cbbc-4146-97ad-e21d7b145ea9"
                  
                  IMPORTANTE: El workflow debe estar ACTIVADO en N8N para que el webhook funcione.
    """
    webhook_path: str
    payload: Dict[str, Any] = {}


class N8NTriggerResponse(BaseModel):
    """Response de disparar un workflow."""
    task_id: str
    status: str
    message: Optional[str] = None


class TaskStatusResponse(BaseModel):
    """Response del estado de una tarea."""
    task_id: str
    state: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

