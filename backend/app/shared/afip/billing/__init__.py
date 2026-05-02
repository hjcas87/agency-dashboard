"""WSFEv1 invoice / credit-note / debit-note authorization.

Public entrypoints:

- `BillingService` — authorize a receipt and persist `AfipInvoiceLog`.
- `CreditNoteService` — same wire call, but enforces ND/NC-specific
  invariants at the type level so callers cannot forget them.

Implementation is split across:

- `request.py` — pure XML builders (no IO, no state).
- `response.py` — pure XML parsers.
- `validations.py` — pre-AFIP validation pipeline.
- `service.py` — `BillingService` orchestrator (the only IO surface).
- `credit_note.py` — `CreditNoteService` wrapper.
"""
