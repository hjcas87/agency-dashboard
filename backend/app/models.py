"""Centralized SQLAlchemy model registry.

Importing this module is what binds every mapped class to
`Base.metadata`. SQLAlchemy resolves cross-feature relationships by
class name, so EVERY model class must be loaded before any code calls
`Base.metadata.create_all()` or runs an Alembic autogenerate diff —
otherwise unrelated tables go missing or relationships fail to bind.

Add new feature models to the imports below AND to `__all__`.

Why no per-line `# noqa: F401`: the names below are re-exported via
`__all__`, which ruff treats as "used". That's the canonical way to
declare a side-effect-import registry without scattering suppression
comments — each `# noqa` reads like surrender, `__all__` reads like
intent."""

from app.core.features.users.models import User
from app.custom.features.activities.models import Activity
from app.custom.features.clients.models import Client, ClientEmail
from app.custom.features.invoices.models import Invoice
from app.custom.features.proposals.models import Proposal, ProposalTask
from app.shared.afip.models import AfipInvoiceLog, AfipToken
from app.shared.email.models import EmailTemplate
from app.shared.pdf.models import PdfTemplate

__all__ = [
    "Activity",
    "AfipInvoiceLog",
    "AfipToken",
    "Client",
    "ClientEmail",
    "EmailTemplate",
    "Invoice",
    "PdfTemplate",
    "Proposal",
    "ProposalTask",
    "User",
]
