"""
Export tasks for easy importing.
Maintained for backward compatibility.
Tasks should be imported directly from their feature modules.

Note: Direct imports from this module are removed to avoid circular import issues.
Import tasks directly from their feature modules:
- from app.core.features.auth.tasks import send_email_task
- from app.core.features.n8n.tasks import trigger_n8n_workflow
"""

# Tasks are auto-discovered by Celery, no need to import them here
__all__ = []
