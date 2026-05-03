"""
Feature de Autenticación.
"""
from fastapi import APIRouter

from app.core.features.auth.routes import router

__all__ = ["router"]
