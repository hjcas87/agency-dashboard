"""
Shared utility functions.
"""
import json
from typing import Any


def safe_json_loads(data: str) -> dict[str, Any]:
    """Safely parse JSON string."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return {}


def format_error_message(error: Exception) -> str:
    """Format exception message for API responses."""
    return str(error) if error else "Unknown error"
