"""Pydantic schemas (request DTOs) and dataclass results (outputs) for the
AFIP/ARCA integration.

Inputs use Pydantic so we get validation at the boundary; outputs use
plain dataclasses because they're internal — no validation cost on the
return path. Using `Decimal` for all monetary amounts is non-negotiable;
floats lose precision in tax calculations.
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.shared.afip.constants import CBU_LENGTH, CUIT_LENGTH
from app.shared.afip.enums import (
    CancellationFlag,
    Concept,
    CurrencyId,
    DocType,
    IvaAliquotId,
    IvaCondition,
    ReceiptType,
    TransferType,
    is_class_c,
    is_fce,
    is_invoice,
    is_note,
)

# ---------------------------------------------------------------------------
# Request DTOs
# ---------------------------------------------------------------------------

# Money type: 13 integer digits + 2 decimal places per ARCA spec.
Money = Annotated[Decimal, Field(ge=Decimal("0"), max_digits=15, decimal_places=2)]


class IvaBlock(BaseModel):
    """One row of the `Iva` array of `FECAEDetRequest`. Multi-aliquot
    invoices need one block per aliquot used."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    aliquot_id: IvaAliquotId
    base_amount: Money
    amount: Money


class AssociatedReceipt(BaseModel):
    """One row of `CbtesAsoc` for a credit/debit note. The class letter of
    the associated receipt must match the issuing note's class (validated
    at the service level)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    receipt_type: ReceiptType
    point_of_sale: int = Field(ge=1, le=99999)
    receipt_number: int = Field(ge=1)
    issue_date: date | None = None
    issuer_cuit: str | None = None

    @field_validator("issuer_cuit")
    @classmethod
    def _validate_cuit(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.replace("-", "").replace(" ", "")
        if not cleaned.isdigit() or len(cleaned) != CUIT_LENGTH:
            raise ValueError("issuer_cuit must be 11 digits")
        return cleaned


class FceData(BaseModel):
    """FCE-specific fields. Required when issuing FCE receipts (validated
    by `model_validator` on the request)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cbu: str | None = None
    alias: str | None = None
    transfer_type: TransferType | None = None
    cancellation: CancellationFlag | None = None
    payment_due_date: date | None = None
    commercial_reference: str | None = None

    @field_validator("cbu")
    @classmethod
    def _validate_cbu(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.isdigit() or len(value) != CBU_LENGTH:
            raise ValueError(f"cbu must be {CBU_LENGTH} digits")
        return value


class InvoiceRequest(BaseModel):
    """Request to issue an invoice (or note) via WSFEv1 `FECAESolicitar`.

    The service decides the receipt number from `FECompUltimoAutorizado`;
    the caller does not provide it. The receipt class (A/B/C, FCE or
    standard) is encoded in `receipt_type`.
    """

    model_config = ConfigDict(extra="forbid")

    receipt_type: ReceiptType
    concept: Concept
    document_type: DocType
    document_number: int = Field(ge=0)
    iva_condition: IvaCondition

    issue_date: date
    service_date_from: date | None = None
    service_date_to: date | None = None
    payment_due_date: date | None = None

    base_amount: Money = Decimal("0")
    iva_amount: Money = Decimal("0")
    non_taxable_amount: Money = Decimal("0")  # ImpTotConc
    exempt_amount: Money = Decimal("0")  # ImpOpEx
    taxes_amount: Money = Decimal("0")  # ImpTrib
    total_amount: Money

    iva_blocks: list[IvaBlock] = Field(default_factory=list)
    associated_receipts: list[AssociatedReceipt] = Field(default_factory=list)
    fce: FceData | None = None
    commercial_reference: str | None = Field(default=None, max_length=50)

    currency: CurrencyId = CurrencyId.PES
    currency_quote: Decimal = Field(default=Decimal("1"), gt=0)

    @model_validator(mode="after")
    def _check_consistency(self) -> "InvoiceRequest":
        # Class C cannot carry IVA detail (ARCA 1443 / 10071 / 1438).
        if is_class_c(self.receipt_type):
            non_zero = (self.iva_amount, self.non_taxable_amount, self.exempt_amount)
            if any(v != Decimal("0") for v in non_zero) or self.iva_blocks:
                raise ValueError(
                    "class C receipts cannot include IVA detail or non-taxable / "
                    "exempt amounts (ARCA 1434/1435/1438/1443/10071)"
                )
        # Service concepts require service-window dates.
        services = (Concept.SERVICES, Concept.PRODUCTS_AND_SERVICES)
        if self.concept in services and (
            self.service_date_from is None or self.service_date_to is None
        ):
            raise ValueError("service_date_from and service_date_to required for service concept")
        # Notes require at least one association (with FCE narrowing in service layer).
        if is_note(self.receipt_type) and not self.associated_receipts:
            raise ValueError("credit/debit notes require at least one associated receipt")
        # FCE requires the FceData block; non-FCE must NOT carry it.
        fce_required = is_fce(self.receipt_type)
        if fce_required and self.fce is None:
            raise ValueError("FCE receipts require the fce data block")
        if not fce_required and self.fce is not None:
            raise ValueError("non-FCE receipts must not include the fce data block (ARCA 10169)")
        # FCE invoices need CBU + transfer type (ARCA 10168 / 10216).
        if fce_required and is_invoice(self.receipt_type) and self.fce is not None:
            if self.fce.cbu is None or self.fce.transfer_type is None:
                raise ValueError(
                    "FCE invoices require fce.cbu and fce.transfer_type (ARCA 10168/10216)"
                )
            if self.fce.payment_due_date is None:
                raise ValueError("FCE invoices require fce.payment_due_date (ARCA 10163)")
        # FCE notes need cancellation flag (ARCA 10173).
        if fce_required and is_note(self.receipt_type) and self.fce is not None:
            if self.fce.cancellation is None:
                raise ValueError("FCE credit/debit notes require fce.cancellation (ARCA 10173)")
        # PES currency forbids CanMisMonExt; non-PES enforces it (ARCA 10239/10241).
        # The flag itself is set by the service layer; the caller only sets currency.
        return self


class TaxpayerRequest(BaseModel):
    """Request to query the taxpayer registry (Padrón A5)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cuit: str

    @field_validator("cuit")
    @classmethod
    def _validate_cuit(cls, value: str) -> str:
        cleaned = value.replace("-", "").replace(" ", "")
        if not cleaned.isdigit() or len(cleaned) != CUIT_LENGTH:
            raise ValueError("cuit must be 11 digits")
        return cleaned


class LastAuthorizedRequest(BaseModel):
    """Request to fetch the last authorized invoice number for a
    (receipt_type, point_of_sale) pair (defaults to the configured
    point of sale)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    receipt_type: ReceiptType
    point_of_sale: int | None = Field(default=None, ge=1, le=99999)


# ---------------------------------------------------------------------------
# Result dataclasses (outputs)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AfipObservation:
    """Non-blocking note returned by ARCA (e.g. 10217, 10234, 10237)."""

    code: int
    message: str


@dataclass(frozen=True, slots=True)
class AfipError:
    """Blocking error returned by ARCA inside a syntactically valid response."""

    code: int
    message: str


@dataclass(frozen=True, slots=True)
class InvoiceResult:
    """Outcome of an authorize-invoice / authorize-note call. `success`
    is False whenever ARCA returned `Resultado=R` or any error list is
    non-empty even with `Resultado=A` (defensive)."""

    success: bool
    receipt_type: ReceiptType
    point_of_sale: int
    receipt_number: int | None
    cae: str | None
    cae_expiration: date | None
    authorized_cbte_tipo: int | None
    observations: list[AfipObservation] = field(default_factory=list)
    errors: list[AfipError] = field(default_factory=list)
    raw_response: str | None = None
    log_id: int | None = None


@dataclass(frozen=True, slots=True)
class FiscalDomicile:
    address: str | None
    locality: str | None
    province: str | None
    province_id: str | None
    postal_code: str | None
    domicile_type: str | None


@dataclass(frozen=True, slots=True)
class TaxpayerActivity:
    activity_id: str | None
    description: str | None
    nomenclature: str | None
    order: str | None
    period: str | None


@dataclass(frozen=True, slots=True)
class TaxpayerTax:
    tax_id: str | None
    description: str | None
    status: str | None
    reason: str | None
    period: str | None


@dataclass(frozen=True, slots=True)
class TaxpayerCategory:
    category_id: str | None
    tax_id: str | None
    period: str | None


@dataclass(frozen=True, slots=True)
class MonotributoData:
    activities: list[TaxpayerActivity] = field(default_factory=list)
    categories: list[TaxpayerCategory] = field(default_factory=list)
    taxes: list[TaxpayerTax] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class GeneralRegimeData:
    activities: list[TaxpayerActivity] = field(default_factory=list)
    taxes: list[TaxpayerTax] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TaxpayerInfo:
    """Result of `get_taxpayer`. Mirrors `getPersona_v2` of Padrón A5."""

    person_id: str | None
    first_name: str | None
    last_name: str | None
    company_name: str | None
    person_type: str | None
    key_type: str | None
    status: str | None
    closing_month: str | None
    is_succession: str | None
    date_social_contract: str | None
    fiscal_domicile: FiscalDomicile
    monotributo: MonotributoData
    general_regime: GeneralRegimeData


@dataclass(frozen=True, slots=True)
class LastAuthorizedResult:
    receipt_type: ReceiptType
    point_of_sale: int
    last_number: int


__all__ = [
    "AfipError",
    "AfipObservation",
    "AssociatedReceipt",
    "FceData",
    "FiscalDomicile",
    "GeneralRegimeData",
    "InvoiceRequest",
    "InvoiceResult",
    "IvaBlock",
    "LastAuthorizedRequest",
    "LastAuthorizedResult",
    "MonotributoData",
    "Money",
    "TaxpayerActivity",
    "TaxpayerCategory",
    "TaxpayerInfo",
    "TaxpayerRequest",
    "TaxpayerTax",
]
