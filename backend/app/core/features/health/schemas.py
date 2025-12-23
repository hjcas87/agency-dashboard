"""
Schemas para el feature de health check.
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional


class HealthResponse(BaseModel):
    """Response de health check."""
    status: str
    module: str
    details: Optional[Dict[str, Any]] = None

