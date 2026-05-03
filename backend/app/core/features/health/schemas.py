"""
Schemas para el feature de health check.
"""
from typing import Any, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response de health check."""

    status: str
    module: str
    details: Optional[dict[str, Any]] = None
