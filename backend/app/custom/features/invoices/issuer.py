"""Issuer (emisor) data for the printed Factura PDF.

This file is the **only** place that knows about a particular client's
identity — the agency's name, address, IVA condition, CUIT, gross-
income code, activity start date, optional logo path. Everything else
in the invoicing flow is data-driven.

To re-use this PDF in a different project: copy
`backend/app/custom/features/invoices/issuer.py` to the new project
and overwrite the `ISSUER` constant with that project's data. The
renderer in `shared/pdf/renderers/invoice.py` is agnostic — it accepts
any IssuerData shape.

The dataclass shape itself is defined once here; if it ever needs to
move into `shared/`, that's a refactor, not a re-implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True, slots=True)
class IssuerData:
    """Static facts about the entity that emits the invoice."""

    legal_name: str  # "Razón Social" — appears at the top
    address: str  # "Domicilio Comercial"
    iva_condition_label: str  # "Responsable Monotributo" / "IVA Responsable Inscripto" / etc.
    cuit: str  # 11 digits, no separators
    gross_income: str  # "Ingresos Brutos" — convenio multilateral or local code
    activity_start_date: date  # "Fecha de Inicio de Actividades"
    logo_path: Path | None = None  # absolute path to a PNG/JPG to embed top-left


# --- Hardcoded for this project ------------------------------------------
# Replace these with your own data when reusing the renderer.

ISSUER = IssuerData(
    legal_name="CARRIEGO ESTELLANO LEANDRO ANGEL",
    address="Río Gualeguay 491 - Villa Valdense, Buenos Aires",
    iva_condition_label="Responsable Monotributo",
    cuit="20410646243",
    gross_income="20410646243",
    activity_start_date=date(2024, 5, 1),
    logo_path=None,
)


__all__ = ["ISSUER", "IssuerData"]
