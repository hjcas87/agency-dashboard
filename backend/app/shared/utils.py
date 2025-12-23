"""
Shared utility functions.
"""
from typing import Any, Dict
import json


def safe_json_loads(data: str) -> Dict[str, Any]:
    """Safely parse JSON string."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return {}


def format_error_message(error: Exception) -> str:
    """Format exception message for API responses."""
    return str(error) if error else "Unknown error"

