"""
Export tasks for easy importing.
Maintained for backward compatibility.
Tasks should be imported directly from their feature modules.
"""
from app.core.features.n8n.tasks import trigger_n8n_workflow
from app.core.features.auth.tasks import send_email_task

__all__ = ["trigger_n8n_workflow", "send_email_task"]
