"""Domain enums for the AFIP/ARCA integration.

Every domain literal lives here. Inline string/int literals in business
logic fail review (see `README.md` — coding conventions).

Source of truth for receipt-type / IVA-condition compatibility is the
**runtime** of `FEParamGetCondicionIvaReceptor` (verified Apr 2026,
documented in `docs/references/afip/manual_dev.md`). The written annex of
the manual disagrees in places; the runtime wins.
"""
from enum import IntEnum, StrEnum


class AfipEnvironment(StrEnum):
    """ARCA environment selector. Drives the URLs in `constants.py`."""

    HOMO = "homo"
    PROD = "prod"


class Concept(IntEnum):
    """`Concepto` field of `FECAEDetRequest` (ARCA code 713)."""

    PRODUCTS = 1
    SERVICES = 2
    PRODUCTS_AND_SERVICES = 3


class DocType(IntEnum):
    """`DocTipo` of `FECAEDetRequest`. Subset of values returned by
    `FEParamGetTiposDoc`. Extend when needed (legacy module did not cover
    foreign-doc types 30/91/94 — kept out until a real case lands)."""

    CUIT = 80
    CUIL = 86
    CDI = 87
    DNI = 96
    FINAL_CONSUMER = 99


class IvaAliquotId(IntEnum):
    """`AlicIva.Id` (catalog from `FEParamGetTiposIva`).

    Initial port keeps a single aliquot path (legacy module was hardcoded
    to GENERAL=21%). Multi-aliquot support is a follow-up PR."""

    EXEMPT = 3  # 0%
    REDUCED = 4  # 10.5%
    GENERAL = 5  # 21%
    INCREASED = 6  # 27%
    REDUCED_5 = 8  # 5%
    REDUCED_2_5 = 9  # 2.5%


class IvaCondition(StrEnum):
    """Receiver IVA condition as known by the consumer of the agency dashboard.

    Mapped to ARCA's `CondicionIVAReceptorId` (RG 5616) in
    `IVA_CONDITION_TO_AFIP_CODE`. Distinct from the receipt's `letter` —
    this is *who the receiver is*, not *which receipt is being issued*.
    """

    RI = "RI"  # Responsable Inscripto
    MT = "MT"  # Monotributista
    EX = "EX"  # IVA Exento
    NA = "NA"  # IVA No Alcanzado
    CF = "CF"  # Consumidor Final
    NC = "NC"  # No Categorizado


# Mapping IvaCondition -> CondicionIVAReceptorId (RG 5616).
# These ARCA codes are the values returned by `FEParamGetCondicionIvaReceptor`.
# Legacy bug 1: NA was mapped to 3 (does not exist in ARCA); now 15.
IVA_CONDITION_TO_AFIP_CODE: dict[IvaCondition, int] = {
    IvaCondition.RI: 1,
    IvaCondition.EX: 4,
    IvaCondition.CF: 5,
    IvaCondition.MT: 6,
    IvaCondition.NC: 7,
    IvaCondition.NA: 15,
}


class ReceiptLetter(StrEnum):
    """The class letter of a receipt — encodes who can receive it."""

    A = "A"
    B = "B"
    C = "C"


class ReceiptType(IntEnum):
    """`CbteTipo` for the receipts the agency emits.

    Values match `FEParamGetTiposCbte`. Class M (51..54) and bienes-usados
    (49) are intentionally not included — the agency does not emit them
    and the legacy module did not support them either."""

    INVOICE_A = 1
    DEBIT_NOTE_A = 2
    CREDIT_NOTE_A = 3
    INVOICE_B = 6
    DEBIT_NOTE_B = 7
    CREDIT_NOTE_B = 8
    INVOICE_C = 11
    DEBIT_NOTE_C = 12
    CREDIT_NOTE_C = 13

    FCE_INVOICE_A = 201
    FCE_DEBIT_NOTE_A = 202
    FCE_CREDIT_NOTE_A = 203
    FCE_INVOICE_B = 206
    FCE_DEBIT_NOTE_B = 207
    FCE_CREDIT_NOTE_B = 208
    FCE_INVOICE_C = 211
    FCE_DEBIT_NOTE_C = 212
    FCE_CREDIT_NOTE_C = 213


# Receipt classification — derived once, accessed via lookup tables to avoid
# nested if/else in business logic.
_FCE_RECEIPTS: frozenset[ReceiptType] = frozenset(
    rt for rt in ReceiptType if rt.name.startswith("FCE_")
)
_CREDIT_NOTES: frozenset[ReceiptType] = frozenset(
    rt for rt in ReceiptType if "CREDIT_NOTE" in rt.name
)
_DEBIT_NOTES: frozenset[ReceiptType] = frozenset(
    rt for rt in ReceiptType if "DEBIT_NOTE" in rt.name
)
_INVOICES: frozenset[ReceiptType] = frozenset(rt for rt in ReceiptType if "INVOICE" in rt.name)


def is_fce(receipt: ReceiptType) -> bool:
    """True if the receipt is part of the MiPyMEs FCE regime."""
    return receipt in _FCE_RECEIPTS


def is_credit_note(receipt: ReceiptType) -> bool:
    return receipt in _CREDIT_NOTES


def is_debit_note(receipt: ReceiptType) -> bool:
    return receipt in _DEBIT_NOTES


def is_invoice(receipt: ReceiptType) -> bool:
    return receipt in _INVOICES


def is_note(receipt: ReceiptType) -> bool:
    return is_credit_note(receipt) or is_debit_note(receipt)


def receipt_letter(receipt: ReceiptType) -> ReceiptLetter:
    """The trailing class letter (A/B/C) inferred from the enum name."""
    return ReceiptLetter(receipt.name[-1])


def is_class_c(receipt: ReceiptType) -> bool:
    return receipt_letter(receipt) is ReceiptLetter.C


def requires_iva_block(receipt: ReceiptType) -> bool:
    """Class A and B (and their FCE variants) require the IVA detail
    block; class C must not include it (ARCA codes 1443 / 10071)."""
    return not is_class_c(receipt)


# Allowed receivers per receipt class — direct from ARCA runtime
# (`FEParamGetCondicionIvaReceptor`), Apr 2026.
# Used by the validation pipeline. Kept here so the dispatch table is
# co-located with the enums it references.
_STANDARD_A_RECEIVERS: frozenset[int] = frozenset({1, 6, 13, 16})
_STANDARD_B_RECEIVERS: frozenset[int] = frozenset({4, 5, 7, 8, 9, 10, 15})
_STANDARD_C_RECEIVERS: frozenset[int] = frozenset({1, 4, 5, 6, 7, 8, 9, 10, 13, 15, 16})
_FCE_A_RECEIVERS: frozenset[int] = frozenset({1, 6})
_FCE_BC_RECEIVERS: frozenset[int] = frozenset({1, 4, 6})


_ALLOWED_RECEIVERS_BY_RECEIPT: dict[ReceiptType, frozenset[int]] = {
    ReceiptType.INVOICE_A: _STANDARD_A_RECEIVERS,
    ReceiptType.DEBIT_NOTE_A: _STANDARD_A_RECEIVERS,
    ReceiptType.CREDIT_NOTE_A: _STANDARD_A_RECEIVERS,
    ReceiptType.INVOICE_B: _STANDARD_B_RECEIVERS,
    ReceiptType.DEBIT_NOTE_B: _STANDARD_B_RECEIVERS,
    ReceiptType.CREDIT_NOTE_B: _STANDARD_B_RECEIVERS,
    ReceiptType.INVOICE_C: _STANDARD_C_RECEIVERS,
    ReceiptType.DEBIT_NOTE_C: _STANDARD_C_RECEIVERS,
    ReceiptType.CREDIT_NOTE_C: _STANDARD_C_RECEIVERS,
    ReceiptType.FCE_INVOICE_A: _FCE_A_RECEIVERS,
    ReceiptType.FCE_DEBIT_NOTE_A: _FCE_A_RECEIVERS,
    ReceiptType.FCE_CREDIT_NOTE_A: _FCE_A_RECEIVERS,
    ReceiptType.FCE_INVOICE_B: _FCE_BC_RECEIVERS,
    ReceiptType.FCE_DEBIT_NOTE_B: _FCE_BC_RECEIVERS,
    ReceiptType.FCE_CREDIT_NOTE_B: _FCE_BC_RECEIVERS,
    ReceiptType.FCE_INVOICE_C: _FCE_BC_RECEIVERS,
    ReceiptType.FCE_DEBIT_NOTE_C: _FCE_BC_RECEIVERS,
    ReceiptType.FCE_CREDIT_NOTE_C: _FCE_BC_RECEIVERS,
}


def allowed_afip_codes_for(receipt: ReceiptType) -> frozenset[int]:
    """ARCA `CondicionIVAReceptorId` values accepted as receivers for the
    given receipt type. Empty set means the receipt is unrestricted —
    which never happens for the receipts we emit."""
    return _ALLOWED_RECEIVERS_BY_RECEIPT[receipt]


# Mapping non-FCE invoice -> FCE equivalent (for the optional escalation
# to FCE when conditions force it, ARCA codes 10188/10192/1485).
_INVOICE_TO_FCE: dict[ReceiptType, ReceiptType] = {
    ReceiptType.INVOICE_A: ReceiptType.FCE_INVOICE_A,
    ReceiptType.INVOICE_B: ReceiptType.FCE_INVOICE_B,
    ReceiptType.INVOICE_C: ReceiptType.FCE_INVOICE_C,
}


def to_fce(receipt: ReceiptType) -> ReceiptType:
    """Return the FCE counterpart for a standard invoice; for any
    non-invoice or already-FCE receipt return the input unchanged."""
    return _INVOICE_TO_FCE.get(receipt, receipt)


# Mapping invoice -> credit note / debit note in the same class (used by
# CreditNoteService when the consumer asks for "the NC of this invoice").
_INVOICE_TO_CREDIT_NOTE: dict[ReceiptType, ReceiptType] = {
    ReceiptType.INVOICE_A: ReceiptType.CREDIT_NOTE_A,
    ReceiptType.INVOICE_B: ReceiptType.CREDIT_NOTE_B,
    ReceiptType.INVOICE_C: ReceiptType.CREDIT_NOTE_C,
    ReceiptType.FCE_INVOICE_A: ReceiptType.FCE_CREDIT_NOTE_A,
    ReceiptType.FCE_INVOICE_B: ReceiptType.FCE_CREDIT_NOTE_B,
    ReceiptType.FCE_INVOICE_C: ReceiptType.FCE_CREDIT_NOTE_C,
}


_INVOICE_TO_DEBIT_NOTE: dict[ReceiptType, ReceiptType] = {
    ReceiptType.INVOICE_A: ReceiptType.DEBIT_NOTE_A,
    ReceiptType.INVOICE_B: ReceiptType.DEBIT_NOTE_B,
    ReceiptType.INVOICE_C: ReceiptType.DEBIT_NOTE_C,
    ReceiptType.FCE_INVOICE_A: ReceiptType.FCE_DEBIT_NOTE_A,
    ReceiptType.FCE_INVOICE_B: ReceiptType.FCE_DEBIT_NOTE_B,
    ReceiptType.FCE_INVOICE_C: ReceiptType.FCE_DEBIT_NOTE_C,
}


def credit_note_for(invoice: ReceiptType) -> ReceiptType:
    """The matching credit note for an invoice. Raises `KeyError` if the
    input is not an invoice — by design (callers must validate first)."""
    return _INVOICE_TO_CREDIT_NOTE[invoice]


def debit_note_for(invoice: ReceiptType) -> ReceiptType:
    """The matching debit note for an invoice. Same contract as
    `credit_note_for`."""
    return _INVOICE_TO_DEBIT_NOTE[invoice]


class TransferType(StrEnum):
    """FCE Optional id=27 — only one of these is allowed (ARCA code 10215)."""

    SCA = "SCA"  # Sistema de Circulación Abierta
    ADC = "ADC"  # Agente de Depósito Colectivo


class CancellationFlag(StrEnum):
    """FCE Optional id=22 — annulment marker for ND/NC (ARCA 10167)."""

    YES = "S"
    NO = "N"


class CurrencyId(StrEnum):
    """`MonId` field. Only PES is in scope for the initial port; USD listed
    so the multi-currency follow-up has a place to extend."""

    PES = "PES"
    USD = "USD"


class SameForeignCurrencyMarker(StrEnum):
    """`CanMisMonExt` for non-PES invoices (ARCA 10239 / 10241)."""

    YES = "S"
    NO = "N"


class AfipResult(StrEnum):
    """Header `Resultado` of `FECAESolicitar` response."""

    APPROVED = "A"
    REJECTED = "R"
    PARTIAL = "P"


class TaxStatus(StrEnum):
    """`estado` field of Padrón A5 responses."""

    ACTIVE = "AC"
    EXEMPT = "EX"
    INACTIVE = "BD"
    NOT_INSCRIBED = "NI"


__all__ = [
    "AfipEnvironment",
    "AfipResult",
    "CancellationFlag",
    "Concept",
    "CurrencyId",
    "DocType",
    "IVA_CONDITION_TO_AFIP_CODE",
    "IvaAliquotId",
    "IvaCondition",
    "ReceiptLetter",
    "ReceiptType",
    "SameForeignCurrencyMarker",
    "TaxStatus",
    "TransferType",
    "allowed_afip_codes_for",
    "credit_note_for",
    "debit_note_for",
    "is_class_c",
    "is_credit_note",
    "is_debit_note",
    "is_fce",
    "is_invoice",
    "is_note",
    "receipt_letter",
    "requires_iva_block",
    "to_fce",
]
