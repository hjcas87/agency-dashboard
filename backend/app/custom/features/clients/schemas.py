"""
Pydantic schemas for the Client feature.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.shared.afip.constants import CUIT_LENGTH
from app.shared.afip.enums import IvaCondition


class ClientEmailIn(BaseModel):
    """Inbound payload for one of a client's additional (CC) emails.

    The primary email lives on `Client.email`; this schema only carries
    the secondary recipients that must always be CC'd when reaching out
    (typical: tesorería / administración mailboxes shared with a contact)."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    label: str | None = Field(default=None, max_length=100)


class ClientEmailResponse(BaseModel):
    """Outbound shape for an additional email — `id` is what the form
    uses to keep React keys stable across edits."""

    id: int
    email: str
    label: str | None

    model_config = ConfigDict(from_attributes=True)


def _normalize_cuit(value: str | None) -> str | None:
    """Strip separators (`-`, ` `) from a CUIT and assert 11 digits.
    Mirrors the validator in `app.shared.afip.config.AfipSettings.CUIT`
    and `app.shared.afip.schemas.TaxpayerRequest.cuit` so the rules are
    consistent across the integration."""
    if value is None or value == "":
        return None
    cleaned = value.replace("-", "").replace(" ", "")
    if not cleaned.isdigit() or len(cleaned) != CUIT_LENGTH:
        raise ValueError(f"CUIT must be {CUIT_LENGTH} digits (with or without separators)")
    return cleaned


class ClientCreate(BaseModel):
    """Schema for creating a new client."""

    name: str
    company: str | None = None
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    cuit: str | None = None
    iva_condition: IvaCondition | None = None
    additional_emails: list[ClientEmailIn] = Field(default_factory=list)

    @field_validator("cuit")
    @classmethod
    def _check_cuit(cls, value: str | None) -> str | None:
        return _normalize_cuit(value)


class ClientUpdate(BaseModel):
    """Schema for updating an existing client.

    `additional_emails` is treated as a *full replacement* when present:
    whatever list the operator submits becomes the new set of secondary
    emails. Pass `None` (or omit the field) to leave them untouched.
    """

    name: str | None = None
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    cuit: str | None = None
    iva_condition: IvaCondition | None = None
    additional_emails: list[ClientEmailIn] | None = None

    @field_validator("cuit")
    @classmethod
    def _check_cuit(cls, value: str | None) -> str | None:
        return _normalize_cuit(value)


class ClientResponse(BaseModel):
    """Schema returned for client operations."""

    id: int
    name: str
    company: str | None
    email: str
    phone: str | None
    address: str | None
    cuit: str | None
    iva_condition: IvaCondition | None
    additional_emails: list[ClientEmailResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CuitLookupResponse(BaseModel):
    """Result of `GET /clients/lookup-cuit/{cuit}` — what the operator's
    form pre-fills when the "Buscar en AFIP" button fires.

    Every field is optional: AFIP returns partial data depending on
    whether the CUIT belongs to a person or an entity, and on what
    regimes are active. The frontend only fills inputs that were empty.
    """

    cuit: str
    status: str | None = None  # estadoClave (ACTIVO / INACTIVO / etc.)
    person_type: str | None = None  # FISICA / JURIDICA
    company_name: str | None = None  # razonSocial (typically for JURIDICA)
    first_name: str | None = None
    last_name: str | None = None
    iva_condition: IvaCondition | None = None  # inferred from active taxes; may be None

    # Echo of the address fields so the consumer feature can decide
    # whether to surface them as "address autocomplete" suggestions.
    fiscal_address: str | None = None
    fiscal_locality: str | None = None
    fiscal_province: str | None = None
    fiscal_postal_code: str | None = None
