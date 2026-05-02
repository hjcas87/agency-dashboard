"""Public façade for the AFIP/ARCA integration.

`AfipService` implements `IAfipService` and is the **only** entry point
consumers should depend on. It wires the four collaborators
(`SoapClient`, `AuthService`, `BillingService`, `TaxpayerService`,
`CreditNoteService`) so the consumer just needs a SQLAlchemy session:

    with AfipService(db=session) as afip:
        result = afip.issue_invoice(InvoiceRequest(...))

For FastAPI consumers, prefer the dependency factory below
(`get_afip_service`), which yields an open `AfipService` and closes it
at request end.
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.shared.afip.auth import AuthService
from app.shared.afip.billing.credit_note import CreditNoteService
from app.shared.afip.billing.service import BillingService
from app.shared.afip.config import AfipSettings, afip_settings
from app.shared.afip.schemas import (
    InvoiceRequest,
    InvoiceResult,
    LastAuthorizedRequest,
    LastAuthorizedResult,
    TaxpayerInfo,
    TaxpayerRequest,
)
from app.shared.afip.taxpayer import TaxpayerService
from app.shared.afip.transport import SoapClient
from app.shared.interfaces.afip_service import IAfipService


class AfipService(IAfipService):
    """Single composition root for the integration. Owns the
    `SoapClient`'s lifecycle when one isn't injected; closes it on
    `close()` / context exit."""

    def __init__(
        self,
        db: Session,
        soap_client: SoapClient | None = None,
        settings: AfipSettings = afip_settings,
    ) -> None:
        self._db = db
        self._settings = settings
        self._owns_client = soap_client is None
        self._soap_client = soap_client or SoapClient(
            timeout=settings.TIMEOUT_SECONDS,
            max_retries=settings.MAX_RETRIES,
        )

        self._auth = AuthService(db=db, soap_client=self._soap_client, settings=settings)
        self._billing = BillingService(
            db=db, auth=self._auth, soap_client=self._soap_client, settings=settings
        )
        self._credit_note = CreditNoteService(self._billing)
        self._taxpayer = TaxpayerService(
            auth=self._auth, soap_client=self._soap_client, settings=settings
        )

    # ------------------------------------------------------------------ context

    def __enter__(self) -> AfipService:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Release the SOAP client only if this service created it."""
        if self._owns_client:
            self._soap_client.close()

    # ------------------------------------------------------------------ public API

    def issue_invoice(self, request: InvoiceRequest) -> InvoiceResult:
        return self._billing.issue(request)

    def issue_credit_note(self, request: InvoiceRequest) -> InvoiceResult:
        return self._credit_note.issue_credit_note(request)

    def issue_debit_note(self, request: InvoiceRequest) -> InvoiceResult:
        return self._credit_note.issue_debit_note(request)

    def get_taxpayer(self, request: TaxpayerRequest) -> TaxpayerInfo:
        return self._taxpayer.get(request)

    def get_last_authorized(self, request: LastAuthorizedRequest) -> LastAuthorizedResult:
        return self._billing.get_last_authorized(request)


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------


def get_afip_service(db: Session) -> Generator[AfipService, None, None]:
    """Yield a request-scoped `AfipService` and close it on exit.

    Usage in a FastAPI route::

        from fastapi import Depends
        from app.database import get_db
        from app.shared.afip import AfipService, get_afip_service

        @router.post("/invoices")
        def create_invoice(
            payload: InvoiceRequest,
            afip: AfipService = Depends(lambda db=Depends(get_db): get_afip_service(db)),
        ) -> InvoiceResult:
            return afip.issue_invoice(payload)

    This dependency is part of `shared/afip/` so consumer features do
    not have to duplicate the wiring."""
    afip = AfipService(db=db)
    try:
        yield afip
    finally:
        afip.close()


__all__ = ["AfipService", "get_afip_service"]
