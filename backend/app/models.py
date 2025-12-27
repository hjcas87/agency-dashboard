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
    from app.custom.features.pipelines.models import Pipeline, PipelineStage  # noqa: F401
except ImportError:
    pass

# Lead model needs to be imported before Opportunity (which references it)
try:
    from app.custom.features.leads.models import Lead, Touchpoint  # noqa: F401
except ImportError:
    pass

# Then import models that depend on the above models
try:
    from app.custom.features.opportunities.models import Opportunity  # noqa: F401
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
