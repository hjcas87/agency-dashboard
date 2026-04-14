"""
Centralized model imports.

Import all models here to ensure SQLAlchemy can resolve relationships.
Custom features should register their models in this file as they are created.
"""

# Core models
from app.core.features.users.models import User  # noqa: F401

# Custom models
from app.custom.features.clients.models import Client  # noqa: F401
from app.custom.features.proposals.models import Proposal, ProposalTask  # noqa: F401
from app.shared.pdf.models import PdfTemplate  # noqa: F401
from app.shared.email.models import EmailTemplate  # noqa: F401
