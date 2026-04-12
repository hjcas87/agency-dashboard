"""
Centralized model imports.

Import all models here to ensure SQLAlchemy can resolve relationships.
Custom features should register their models in this file as they are created.
"""

# Core models
from app.core.features.users.models import User  # noqa: F401

# Custom models — add imports here as features are created:
# from app.custom.features.<feature>.models import <Model>  # noqa: F401
