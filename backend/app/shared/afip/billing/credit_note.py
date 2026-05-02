"""Credit-note / debit-note wrapper around `BillingService`.

Same wire call as a regular invoice (`FECAESolicitar`), but ARCA imposes
extra structural rules on notes that this service enforces locally
*before* hitting the network — better UX (Spanish error message,
specific code) and one fewer round-trip.

Rules captured here:
- The note's class letter (A / B / C) must match every associated
  receipt's class letter (ARCA 10040).
- The note's `issue_date` must be on or after every associated
  receipt's `issue_date` (ARCA 10210 / "fecha de la nota debe ser >=
  fecha del asociado"). Skipped per-association when the consumer
  doesn't know the associated date.

Rules **not** captured here:
- Same-month-and-year requirement (ARCA 10210 case 2): only fires
  when the associated receipt's date is *posterior* to the note's
  date. Edge case; ARCA's rejection is informative enough.
- NC monto > asociado (observation 10237): we'd need to call
  FECompConsultar against the associated receipt to know its total.
  Left as an ARCA-side observation.
- FCE annulment association rules (10183 / 10186 / 10187 / 10193):
  too specific. ARCA enforces them server-side.
"""
from __future__ import annotations

from app.shared.afip.billing.service import BillingService
from app.shared.afip.enums import is_note, receipt_letter
from app.shared.afip.exceptions import AfipValidationError
from app.shared.afip.messages import ERR_AFIP_VALIDATION_COMBINED
from app.shared.afip.schemas import InvoiceRequest, InvoiceResult


class CreditNoteService:
    """Thin wrapper that delegates to `BillingService.issue` after
    note-specific validation."""

    def __init__(self, billing: BillingService) -> None:
        self._billing = billing

    def issue_credit_note(self, request: InvoiceRequest) -> InvoiceResult:
        """Authorize a credit note (`CREDIT_NOTE_*` or
        `FCE_CREDIT_NOTE_*`)."""
        _enforce_note_rules(request, expected_kind="credit_note")
        return self._billing.issue(request)

    def issue_debit_note(self, request: InvoiceRequest) -> InvoiceResult:
        """Authorize a debit note (`DEBIT_NOTE_*` or
        `FCE_DEBIT_NOTE_*`)."""
        _enforce_note_rules(request, expected_kind="debit_note")
        return self._billing.issue(request)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _enforce_note_rules(request: InvoiceRequest, *, expected_kind: str) -> None:
    """Validate note-specific rules. Raises `AfipValidationError`
    accumulating every failure, never silently."""
    failures: list[tuple[int | None, str]] = []

    if not is_note(request.receipt_type):
        failures.append(
            (
                None,
                f"This service only handles credit/debit notes; got "
                f"{request.receipt_type.name}",
            )
        )
    else:
        _check_kind_matches(request, expected_kind, failures)
        _check_associated_class_letter(request, failures)
        _check_associated_date_order(request, failures)

    if failures:
        combined = " | ".join(message for _, message in failures)
        raise AfipValidationError(
            ERR_AFIP_VALIDATION_COMBINED.format(messages=combined),
            errors=failures,
        )


def _check_kind_matches(
    request: InvoiceRequest,
    expected_kind: str,
    failures: list[tuple[int | None, str]],
) -> None:
    """Reject calling `issue_credit_note` with a debit-note request and
    vice versa."""
    name = request.receipt_type.name
    if expected_kind == "credit_note" and "CREDIT_NOTE" not in name:
        failures.append(
            (None, f"issue_credit_note called with {name}; expected a CREDIT_NOTE_* type")
        )
    elif expected_kind == "debit_note" and "DEBIT_NOTE" not in name:
        failures.append(
            (None, f"issue_debit_note called with {name}; expected a DEBIT_NOTE_* type")
        )


def _check_associated_class_letter(
    request: InvoiceRequest,
    failures: list[tuple[int | None, str]],
) -> None:
    """Every associated receipt must share the note's class letter
    (ARCA 10040). Schema already requires at least one association."""
    note_letter = receipt_letter(request.receipt_type)
    for assoc in request.associated_receipts:
        if receipt_letter(assoc.receipt_type) is not note_letter:
            failures.append(
                (
                    10040,
                    f"associated receipt {assoc.receipt_type.name} (class "
                    f"{receipt_letter(assoc.receipt_type).value}) does not match the "
                    f"note's class {note_letter.value}",
                )
            )


def _check_associated_date_order(
    request: InvoiceRequest,
    failures: list[tuple[int | None, str]],
) -> None:
    """Note's `issue_date` must be >= every associated receipt's
    `issue_date` when known."""
    for assoc in request.associated_receipts:
        if assoc.issue_date is None:
            continue
        if assoc.issue_date > request.issue_date:
            failures.append(
                (
                    10210,
                    f"note date {request.issue_date.isoformat()} cannot be earlier "
                    f"than associated receipt date {assoc.issue_date.isoformat()}",
                )
            )


__all__ = ["CreditNoteService"]
