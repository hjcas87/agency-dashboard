"""Pre-AFIP validation pipeline.

A list of pure validator functions, each `(InvoiceRequest) -> ValidationError | None`.
The orchestrator runs them all and surfaces the combined failure as a
single `AfipValidationError` carrying the list of (ARCA code, friendly
message) pairs — never lets a request that we know ARCA will reject hit
the wire.

Schema-level invariants (class C amount-block, FCE structure, services
date window, notes-need-associations) live in the `InvoiceRequest`
`model_validator` and run at construction time. The validators here
cover the *cross-field* and *runtime* rules that depend on the AFIP
matrices (allowed receivers per receipt class, document-type per
receipt class, the No Categorizado special cases) — i.e. anything
that needs the ARCA reference tables to evaluate.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.shared.afip.constants import CUIT_LENGTH, NO_CATEGORIZADO_CUIT
from app.shared.afip.enums import (
    IVA_CONDITION_TO_AFIP_CODE,
    DocType,
    allowed_afip_codes_for,
    is_fce,
    receipt_letter,
)
from app.shared.afip.exceptions import AfipValidationError
from app.shared.afip.messages import (
    ERR_AFIP_VALIDATION_COMBINED,
    receipt_suggestion_for,
    translate_afip_error,
)
from app.shared.afip.schemas import InvoiceRequest


@dataclass(frozen=True, slots=True)
class ValidationError:
    """One failure surfaced by a validator. `code` is the ARCA code
    the rule maps to (so the friendly message lookup works); `message`
    is the operator-facing string already translated."""

    code: int
    message: str


Validator = Callable[[InvoiceRequest], ValidationError | None]


# ---------------------------------------------------------------------------
# Individual validators — each is a pure function.
# ---------------------------------------------------------------------------


def receipt_iva_compatibility(request: InvoiceRequest) -> ValidationError | None:
    """Receiver IVA condition must be in the allowed set for the
    receipt class (ARCA 10243 / 1474 / 10177)."""
    afip_code = IVA_CONDITION_TO_AFIP_CODE[request.iva_condition]
    if afip_code in allowed_afip_codes_for(request.receipt_type):
        return None
    return ValidationError(
        code=10243,
        message=translate_afip_error(10243, iva_condition=request.iva_condition),
    )


def cuit_required_for_class_a(request: InvoiceRequest) -> ValidationError | None:
    """Class A receipts require DocTipo = 80 (CUIT) in the receiver
    (ARCA 10013 / 1403)."""
    if receipt_letter(request.receipt_type).value != "A":
        return None
    if request.document_type is DocType.CUIT:
        return None
    return ValidationError(code=10013, message=translate_afip_error(10013))


def cuit_required_for_fce(request: InvoiceRequest) -> ValidationError | None:
    """FCE receipts require DocTipo = 80 (CUIT) — ARCA 1487."""
    if not is_fce(request.receipt_type):
        return None
    if request.document_type is DocType.CUIT:
        return None
    return ValidationError(code=1487, message=translate_afip_error(1487))


def fce_no_categorizado(request: InvoiceRequest) -> ValidationError | None:
    """FCE forbids CUIT 23000000000 (No Categorizado) — ARCA 10178/1475."""
    if not is_fce(request.receipt_type):
        return None
    if str(request.document_number) != NO_CATEGORIZADO_CUIT:
        return None
    return ValidationError(code=10178, message=translate_afip_error(10178))


def no_categorizado_requires_taxes(request: InvoiceRequest) -> ValidationError | None:
    """Non-FCE class B with No Categorizado receiver and a high amount
    requires ImpTrib > 0 (ARCA 10067 / 1425)."""
    if str(request.document_number) != NO_CATEGORIZADO_CUIT:
        return None
    if is_fce(request.receipt_type):
        # FCE rejection takes priority — fce_no_categorizado handles it.
        return None
    if request.taxes_amount > 0:
        return None
    return ValidationError(code=10067, message=translate_afip_error(10067))


def document_number_length(request: InvoiceRequest) -> ValidationError | None:
    """Basic format validation per `DocTipo`. Mirrors ARCA 10015 cases."""
    if request.document_type is DocType.FINAL_CONSUMER:
        return None
    raw = str(request.document_number)
    expected = _expected_doc_length(request.document_type)
    if expected is None:
        return None
    if expected[0] <= len(raw) <= expected[1] and raw.isdigit():
        return None
    return ValidationError(code=10015, message=translate_afip_error(10015))


# Per-DocType length range (inclusive) for the formats this module
# supports today. Foreign-doc types deferred to the multi-doc-types PR.
_DOC_LENGTH_RANGES: dict[DocType, tuple[int, int]] = {
    DocType.CUIT: (CUIT_LENGTH, CUIT_LENGTH),
    DocType.CUIL: (CUIT_LENGTH, CUIT_LENGTH),
    DocType.CDI: (CUIT_LENGTH, CUIT_LENGTH),
    DocType.DNI: (7, 8),
}


def _expected_doc_length(doc_type: DocType) -> tuple[int, int] | None:
    return _DOC_LENGTH_RANGES.get(doc_type)


# ---------------------------------------------------------------------------
# Pipeline — append-only list, run in order.
# ---------------------------------------------------------------------------

# Order matters when two validators target the same field: more specific
# rules first. Example: fce_no_categorizado runs before
# no_categorizado_requires_taxes because the FCE rejection is hard.
PIPELINE: tuple[Validator, ...] = (
    document_number_length,
    cuit_required_for_class_a,
    cuit_required_for_fce,
    fce_no_categorizado,
    no_categorizado_requires_taxes,
    receipt_iva_compatibility,
)


def run_pipeline(request: InvoiceRequest) -> list[ValidationError]:
    """Run every validator and return the failures. Empty list = pass."""
    failures: list[ValidationError] = []
    for validator in PIPELINE:
        error = validator(request)
        if error is not None:
            failures.append(error)
    return failures


def raise_on_failures(request: InvoiceRequest) -> None:
    """Run the pipeline and raise `AfipValidationError` if anything fails.

    The exception's `errors` attribute carries the list of `(code,
    message)` pairs; the message itself is the combined Spanish text
    suitable for surfacing to the operator."""
    failures = run_pipeline(request)
    if not failures:
        return
    combined_text = " | ".join(f.message for f in failures)
    raise AfipValidationError(
        ERR_AFIP_VALIDATION_COMBINED.format(messages=combined_text),
        errors=[(f.code, f.message) for f in failures],
    )


__all__ = [
    "PIPELINE",
    "ValidationError",
    "Validator",
    "cuit_required_for_class_a",
    "cuit_required_for_fce",
    "document_number_length",
    "fce_no_categorizado",
    "no_categorizado_requires_taxes",
    "raise_on_failures",
    "receipt_iva_compatibility",
    "receipt_suggestion_for",  # re-exported for callers that need it
    "run_pipeline",
]
