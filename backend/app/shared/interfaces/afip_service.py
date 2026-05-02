"""Public interface for the AFIP/ARCA integration.

Defined here (instead of inside `shared/afip/`) so consumers can depend
on the abstract contract without importing the concrete implementation.
This is the same pattern as `IEmailService` / `IMessageBroker` in this
package."""
from abc import ABC, abstractmethod

from app.shared.afip.schemas import (
    InvoiceRequest,
    InvoiceResult,
    LastAuthorizedRequest,
    LastAuthorizedResult,
    TaxpayerInfo,
    TaxpayerRequest,
)


class IAfipService(ABC):
    """Sync interface (FastAPI routes call this directly; no async
    awaiting on AFIP's SOAP endpoints)."""

    @abstractmethod
    def issue_invoice(self, request: InvoiceRequest) -> InvoiceResult:
        """Authorize an invoice via WSFEv1 `FECAESolicitar`. Persists
        an `AfipInvoiceLog` row regardless of outcome and returns its
        id in the result."""

    @abstractmethod
    def issue_credit_note(self, request: InvoiceRequest) -> InvoiceResult:
        """Authorize a credit note. Same wire call as `issue_invoice`,
        kept as a separate method so the type system can enforce the
        association requirement at the call site."""

    @abstractmethod
    def issue_debit_note(self, request: InvoiceRequest) -> InvoiceResult:
        """Authorize a debit note. Sibling of `issue_credit_note`."""

    @abstractmethod
    def get_taxpayer(self, request: TaxpayerRequest) -> TaxpayerInfo:
        """Query Padrón A5 by CUIT."""

    @abstractmethod
    def get_last_authorized(self, request: LastAuthorizedRequest) -> LastAuthorizedResult:
        """Last authorized receipt number for a (receipt_type, pto.vta)
        pair. Used by the service to compute the next number."""
