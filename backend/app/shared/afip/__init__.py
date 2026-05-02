"""Reusable AFIP/ARCA electronic invoicing integration.

Public API — consumers should import only from this package, never from
submodules. Direct imports from `auth`, `transport`, `billing`,
`taxpayer` are an abstraction leak.

See `README.md` in this directory for the design rationale and
`docs/references/afip/manual_dev.md` for the normative ARCA reference.
"""
from app.shared.afip.config import AfipSettings, afip_settings
from app.shared.afip.enums import (
    CancellationFlag,
    Concept,
    CurrencyId,
    DocType,
    IvaAliquotId,
    IvaCondition,
    ReceiptLetter,
    ReceiptType,
    TransferType,
)
from app.shared.afip.exceptions import (
    AfipAuthenticationError,
    AfipConfigurationError,
    AfipException,
    AfipNetworkError,
    AfipServiceError,
    AfipValidationError,
)
from app.shared.afip.schemas import (
    AfipError,
    AfipObservation,
    AssociatedReceipt,
    FceData,
    FiscalDomicile,
    GeneralRegimeData,
    InvoiceRequest,
    InvoiceResult,
    IvaBlock,
    LastAuthorizedRequest,
    LastAuthorizedResult,
    MonotributoData,
    TaxpayerActivity,
    TaxpayerCategory,
    TaxpayerInfo,
    TaxpayerRequest,
    TaxpayerTax,
)
from app.shared.afip.service import AfipService, get_afip_service

__all__ = [
    "AfipAuthenticationError",
    "AfipConfigurationError",
    "AfipError",
    "AfipException",
    "AfipNetworkError",
    "AfipObservation",
    "AfipService",
    "AfipServiceError",
    "AfipSettings",
    "AfipValidationError",
    "AssociatedReceipt",
    "CancellationFlag",
    "Concept",
    "CurrencyId",
    "DocType",
    "FceData",
    "FiscalDomicile",
    "GeneralRegimeData",
    "InvoiceRequest",
    "InvoiceResult",
    "IvaAliquotId",
    "IvaBlock",
    "IvaCondition",
    "LastAuthorizedRequest",
    "LastAuthorizedResult",
    "MonotributoData",
    "ReceiptLetter",
    "ReceiptType",
    "TaxpayerActivity",
    "TaxpayerCategory",
    "TaxpayerInfo",
    "TaxpayerRequest",
    "TaxpayerTax",
    "TransferType",
    "afip_settings",
    "get_afip_service",
]
