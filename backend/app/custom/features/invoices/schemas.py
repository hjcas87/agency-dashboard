"""Pydantic schemas for the Invoice feature."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.shared.afip.enums import Concept


class InvoiceLineItem(BaseModel):
    """One billable line in a manual invoice. The proposal-driven flow
    snapshots existing tasks into this same shape."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)


class IssueFromProposalRequest(BaseModel):
    """Operator request to invoice an existing proposal as Factura C."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: int = Field(ge=1)
    issue_date: date
    concept: Concept = Concept.PRODUCTS
    service_date_from: date | None = None
    service_date_to: date | None = None
    commercial_reference: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _check_service_dates(self) -> "IssueFromProposalRequest":
        services = (Concept.SERVICES, Concept.PRODUCTS_AND_SERVICES)
        if self.concept in services and (
            self.service_date_from is None or self.service_date_to is None
        ):
            raise ValueError(
                "service_date_from y service_date_to son obligatorios para concepto servicios"
            )
        if (
            self.service_date_from
            and self.service_date_to
            and self.service_date_from > self.service_date_to
        ):
            raise ValueError("service_date_from debe ser <= service_date_to")
        return self


class IssueManualRequest(BaseModel):
    """Operator request to invoice a free-form list of lines as Factura
    C, without a proposal. The client either already exists in the CRM
    (`client_id` set) or this request fails — client creation is a
    separate flow."""

    model_config = ConfigDict(extra="forbid")

    client_id: int = Field(ge=1)
    issue_date: date
    concept: Concept = Concept.PRODUCTS
    service_date_from: date | None = None
    service_date_to: date | None = None
    line_items: list[InvoiceLineItem] = Field(min_length=1)
    commercial_reference: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _check_service_dates(self) -> "IssueManualRequest":
        services = (Concept.SERVICES, Concept.PRODUCTS_AND_SERVICES)
        if self.concept in services and (
            self.service_date_from is None or self.service_date_to is None
        ):
            raise ValueError(
                "service_date_from y service_date_to son obligatorios para concepto servicios"
            )
        if (
            self.service_date_from
            and self.service_date_to
            and self.service_date_from > self.service_date_to
        ):
            raise ValueError("service_date_from debe ser <= service_date_to")
        return self


# --- Responses ------------------------------------------------------------


class InvoiceResponse(BaseModel):
    """Persistent invoice as the operator sees it — joins the AFIP log
    fields the UI cares about (CAE / number / status) directly."""

    id: int
    proposal_id: int | None
    client_id: int
    client_name: str | None = None
    receipt_type: int
    concept: int
    issue_date: date
    service_date_from: date | None
    service_date_to: date | None
    total_amount_ars: Decimal
    document_type: int
    document_number: int
    line_items: list[InvoiceLineItem]
    commercial_reference: str | None

    # Pulled from afip_invoice_log via the FK.
    afip_invoice_log_id: int
    cae: str | None = None
    cae_expiration: date | None = None
    afip_success: bool = False
    afip_observations: list[dict] = Field(default_factory=list)
    afip_errors: list[dict] = Field(default_factory=list)
    receipt_number: int | None = None
    point_of_sale: int | None = None

    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @field_validator("line_items", mode="before")
    @classmethod
    def _coerce_line_items(cls, value: object) -> object:
        """JSONB returns list[dict], convert to InvoiceLineItem list."""
        if isinstance(value, list):
            return [
                v if isinstance(v, InvoiceLineItem) else InvoiceLineItem.model_validate(v)
                for v in value
            ]
        return value


class BillableProposalResponse(BaseModel):
    """A proposal that's ACCEPTED and not yet invoiced — what the
    *Presupuestos facturables* tab shows."""

    id: int
    name: str
    client_id: int | None
    client_name: str | None
    total_ars: Decimal
    created_at: str
