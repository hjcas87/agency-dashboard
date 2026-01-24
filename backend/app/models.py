"""
Centralized model imports.
Import all models here to ensure SQLAlchemy can resolve relationships.
This file should be imported before using any models or creating database tables.
Import models in dependency order to avoid relationship resolution issues.
"""

# Core models
from app.core.features.users.models import User  # noqa: F401

# Custom models - import in dependency order to avoid relationship resolution issues
# First import base models without relationships (or with minimal dependencies)
try:
    from app.custom.features.contacts.models import Contact  # noqa: F401
except ImportError:
    pass

try:
    from app.custom.features.campaigns.models import Campaign  # noqa: F401
except ImportError:
    pass

try:
    from app.custom.features.pipelines.models import Pipeline  # noqa: F401
except ImportError:
    pass

# PipelineStage and Opportunity models (Opportunity depends on Contact)
try:
    from app.custom.features.opportunities.models import (  # noqa: F401
        Opportunity,
        PipelineStage,
        StageHistory,
    )
except ImportError:
    pass

# WhatsApp models (depend on Contact)
try:
    from app.custom.features.whatsapp.models import Conversation, Message  # noqa: F401
except ImportError:
    pass

# Lead model needs to be imported before Opportunity (which references it)
try:
    from app.custom.features.leads.models import Lead, Touchpoint  # noqa: F401
except ImportError:
    pass

try:
    from app.custom.features.activities.models import Activity  # noqa: F401
except ImportError:
    pass

try:
    from app.custom.features.journeys.models import Journey  # noqa: F401
except ImportError:
    pass
