# shared/afip — AFIP/ARCA electronic invoicing integration

Reusable wrapper for the Argentine tax agency (AFIP, now ARCA) web services.
Exposes a typed Python API to custom features that need to issue electronic
invoices, credit/debit notes, query the taxpayer registry, or persist the
authentication ticket. Defines **no HTTP routes**: this is a library, not a
feature. Consumers are responsible for routing, auth, persistence of business
entities, and UI.

This module is the FastAPI/SQLAlchemy port of the Django module previously
maintained at `apps/afip/` (still functional in production, kept locally as
read-only reference; path `afip/` is `.gitignore`d).

> **Normative reference**: see `docs/references/afip/manual_dev.md` (ARCA
> manual RG 4291 v4.0, with runtime corrections verified April 2026 against
> `FEParamGetCondicionIvaReceptor`). The runtime is the source of truth when
> it disagrees with the written annex.

---

## Scope

### What `shared/afip/` does

| Capability | AFIP service | Notes |
|---|---|---|
| Authentication ticket lifecycle | WSAA `loginCms` | CMS-signed ticket, 12 h TTL, cached in DB per service |
| Invoice issuance (CAE) | WSFEv1 `FECAESolicitar` | Class A / B / C and FCE MiPyMEs A / B / C |
| Last authorized invoice number | WSFEv1 `FECompUltimoAutorizado` | Per `(CbteTipo, PtoVta)` |
| Invoice consultation | WSFEv1 `FECompConsultar` | Idempotency check after timeouts |
| Credit / debit notes | WSFEv1 `FECAESolicitar` | With `CbtesAsoc`, includes FCE annulment flow |
| Taxpayer registry lookup | `ws_sr_padron_a5` `getPersona_v2` | Returns inscription data, fiscal domicile, monotributo / general regime |
| Parameter introspection | WSFEv1 `FEParam*` | On-demand, optionally cached |

### What `shared/afip/` deliberately does NOT do

- **No HTTP routes.** Consumers expose endpoints in their own feature
  routers and call into `AfipService`.
- **No business `Invoice` entity.** The persistent log of what was sent to
  AFIP lives here (`AfipInvoiceLog`); the business invoice — with its FK to
  whatever drives billing in the consuming feature (a quote, a proposal, an
  order, a manual entry) — lives in the consuming feature
  (`custom/features/invoices/` is the obvious home for the agency dashboard,
  but `shared/afip/` does not know or care about that).
- **No PDF generation.** `shared/pdf/` is the PDF service; consumers wire
  the two together.
- **No retry / scheduling.** If asynchronous retries are required, the
  consumer schedules a Celery task in its own `tasks.py` and calls
  `AfipService` from there.

---

## Module layout

```
backend/app/shared/afip/
├── README.md                    # this file
├── __init__.py                  # exports AfipService, schemas, exceptions
├── config.py                    # AfipSettings — env-bound config
├── constants.py                 # WSAA / WSFEv1 / Padrón URLs, namespaces, IVA codes
├── enums.py                     # ReceiptType, IvaCondition, DocType, Concept, Currency
├── exceptions.py                # AfipException hierarchy
├── messages.py                  # Spanish operator-facing strings + AFIP error map
├── models.py                    # AfipToken, AfipInvoiceLog (SQLAlchemy)
├── schemas.py                   # Pydantic DTOs (request/response)
├── service.py                   # AfipService — public entrypoint
├── auth/
│   ├── __init__.py
│   ├── cms.py                   # CMS signing via cryptography (no openssl subprocess)
│   ├── ticket.py                # AuthService — WSAA loginCms + DB cache
│   └── locking.py               # threading-safe singleflight for ticket refresh
├── transport/
│   ├── __init__.py
│   ├── soap.py                  # SoapClient — httpx with SECLEVEL=1 SSL context
│   └── xml.py                   # lxml-based builders / parsers
├── billing/
│   ├── __init__.py
│   ├── request.py               # Pure builders for FECAESolicitar XML
│   ├── response.py              # Pure parsers for FECAESolicitar XML
│   ├── service.py               # BillingService orchestrator
│   ├── credit_note.py           # CreditNoteService (delegates to BillingService)
│   └── validations.py           # Pre-AFIP validation pipeline (functional)
├── taxpayer/
│   ├── __init__.py
│   └── service.py               # TaxpayerService — Padrón A5 wrapper
└── repository.py                # AfipTokenRepository, AfipInvoiceLogRepository
```

Sub-packages by capability rather than one flat module: each capability has
its own purely-functional builders/parsers (testable in isolation) plus a
thin orchestrator that ties IO to validators.

---

## Public API

```python
from app.shared.afip import AfipService
from app.shared.afip.schemas import InvoiceRequest, TaxpayerRequest

afip = AfipService(db=db_session)

# Issue an invoice
result = afip.issue_invoice(InvoiceRequest(...))
# -> InvoiceResult { cae, cae_expiration, invoice_number, observations, errors, log_id }

# Issue a credit note
result = afip.issue_credit_note(CreditNoteRequest(...))

# Query the taxpayer registry
taxpayer = afip.get_taxpayer(TaxpayerRequest(cuit=20123456789))
# -> TaxpayerInfo { person, fiscal_domicile, monotributo, general_regime }

# Query the last authorized invoice number
last_number = afip.get_last_authorized(receipt_type=ReceiptType.INVOICE_A)
```

`AfipService` is a thin orchestrator. Each method:

1. Delegates to a feature-local validator pipeline (pre-AFIP checks).
2. Builds the XML request via a pure builder function.
3. Acquires the WSAA ticket via `AuthService` (cached).
4. POSTs via `SoapClient`.
5. Parses the response via a pure parser function.
6. Persists `AfipInvoiceLog` (success, failure, observations, raw XML).
7. Returns a typed `Result` dataclass.

---

## Persistent state

```python
class AfipToken(Base):
    """Cached WSAA ticket. One row per (service, expiration_time)."""
    id: Mapped[int]
    service: Mapped[str]                  # "wsfe", "ws_sr_constancia_inscripcion"
    token: Mapped[str]                    # opaque
    sign: Mapped[str]                     # opaque
    generation_time: Mapped[datetime]
    expiration_time: Mapped[datetime]     # ~12 h after generation
    created_at: Mapped[datetime]


class AfipInvoiceLog(Base):
    """Audit row for every WSFEv1 attempt — success or failure.
    The business 'Invoice' entity (FK to quote/proposal/order) lives in the
    consuming feature and references this row by FK."""
    id: Mapped[int]
    point_of_sale: Mapped[int]
    receipt_type: Mapped[int]             # CbteTipo
    receipt_number: Mapped[int | None]    # only on success
    cae: Mapped[str | None]
    cae_expiration: Mapped[date | None]
    afip_authorized_cbte_tipo: Mapped[int | None]   # what AFIP authorized (may differ)
    request_xml: Mapped[str]
    response_xml: Mapped[str]
    success: Mapped[bool]
    observations: Mapped[list[dict]]      # JSONB
    errors: Mapped[list[dict]]            # JSONB
    issued_at: Mapped[datetime]
```

The consuming feature's `Invoice` model declares
`afip_log_id: ForeignKey(AfipInvoiceLog.id)` and is responsible for whatever
business semantics apply (cancellation, partial payments, reconciliation,
PDF rendering).

---

## Configuration

All settings are bound to environment variables via `AfipSettings`
(`config.py`), itself merged into `app.config.settings`. Cert and key paths
must point to readable files; the service raises `AfipConfigurationError` at
construction time if they are missing or unreadable.

| Env var | Required | Description |
|---|:---:|---|
| `AFIP_ENVIRONMENT` | yes | `homo` or `prod` |
| `AFIP_CUIT` | yes | Issuer CUIT, 11 digits, no separators |
| `AFIP_POINT_OF_SALE` | yes | Issuer point-of-sale, integer |
| `AFIP_CERT_PATH` | yes | Path to X.509 cert (PEM) |
| `AFIP_KEY_PATH` | yes | Path to private key (PEM) |
| `AFIP_CURRENCY_ID` | no (`PES`) | Default currency for invoices |
| `AFIP_TIMEOUT_SECONDS` | no (`30`) | HTTP timeout |
| `AFIP_MAX_RETRIES` | no (`3`) | HTTP retries (POST only, idempotency must be enforced by `FECompConsultar` before retrying CAE requests) |
| `AFIP_TOKEN_REFRESH_THRESHOLD_MINUTES` | no (`30`) | Refresh ticket if it expires within this window |
| `AFIP_RG4444_THRESHOLD_ARS` | no (`0`) | Configurable RG4444 threshold for receiver identification (ARS). Updated manually when ARCA publishes a new value. `0` disables the local check. |

URLs (WSAA, WSFEv1, Padrón) are derived from `AFIP_ENVIRONMENT` in
`constants.py`. They never come from env vars — fixed by AFIP.

### Server deployment checklist

Before the next `make deploy` after this PR is merged, the production server's
`.env` must contain at minimum:

```
AFIP_ENVIRONMENT=prod
AFIP_CUIT=20123456789
AFIP_POINT_OF_SALE=1
AFIP_CERT_PATH=/srv/agency-dashboard/certs/MiCertificado.crt
AFIP_KEY_PATH=/srv/agency-dashboard/certs/MiClavePrivada.key
```

The cert and key files must be uploaded to the path declared above (the
`certs/` folder at the repo root is `.gitignore`d so they never travel via
git). `make deploy` runs `alembic upgrade head` automatically, so the new
tables (`afip_token`, `afip_invoice_log`) are created on first deploy.

---

## Coding conventions enforced in this module

These complement the repo-wide rules in `CLAUDE.md`/`AGENTS.md` and are
non-negotiable in code review for `shared/afip/`:

- **No magic strings.** Every domain literal (XML namespace, SOAP action,
  IVA code, AFIP error code, document type, currency code, cancellation
  marker `"S"` / `"N"`, transfer type `"SCA"` / `"ADC"`, environment marker
  `"homo"` / `"prod"`) is an `Enum` member or a named constant in
  `constants.py`/`enums.py`. Inline string literals in business logic fail
  review.
- **Operator-facing messages live in `messages.py`.** Logic files import
  named constants. Spanish is allowed in `messages.py` (operator UI string).
  All other strings (logger messages, internal names, comments) are English.
- **No nested if/else in business logic.** Pre-AFIP validations are a
  pipeline of pure validator functions
  (`tuple[ValidatorFn, ...]` ⇒ `tuple[ValidationError, ...]`). Receipt type
  / IVA condition compatibility is a dispatch table, not a chain of `if`s.
  Early returns are encouraged.
- **Functional core, imperative shell.** Builders (`xml_for_*`) and parsers
  (`parse_*_response`) are pure and side-effect-free. Side effects (DB,
  network, logging) live in the orchestrator (`service.py`).
- **No mutable shared state.** `AuthService` owns the token cache through
  the repository, never as a class attribute. `BillingService` is
  short-lived per request.
- **80% coverage floor.** Enforced by `pytest --cov-fail-under=80` in
  `pyproject.toml`. New code in this module targets ≥85% (the integration
  is critical and bug-prone). Tests cover: one happy path per receipt
  class (A/B/C/FCE), every validator's failure case, every AFIP error code
  the legacy module already mapped (`messages.AFIP_ERR_*`), CMS signature
  produces the expected DER bytes for a known input, SOAP parser handles
  faults and successful responses, idempotency check via
  `FECompConsultar`.

---

## Out of scope for the initial PR

These are deliberately deferred to keep the first PR reviewable:

- Celery task wrapper for asynchronous retries (consumer-side concern; the
  hooks are exposed but no worker is wired).
- Caching of `FEParam*` responses (cold lookups on every call to start;
  cache layer added when measurement justifies it).
- Multi-line IVA aliquots support (legacy Django bug 4 — the legacy
  module hardcoded 21 %; this port keeps the same constraint and is fixed
  in a follow-up PR specifically for non-21 % rates).
- Multi-currency invoicing (`MonId != PES`) — out of scope for the agency's
  current operation; legacy bug 11 documented but not fixed.
- WSPN (CAEA) flow. Only CAE is implemented (matches legacy module).
- **Dynamic point-of-sale discovery (`FEParamGetPtosVenta`).** This PR
  takes `AFIP_POINT_OF_SALE` from env and treats it as authoritative.
  A follow-up will expose `AfipService.list_points_of_sale()` so consumers
  can render a picker against the CUIT's actually-enabled points of sale,
  removing one hand-edited env var.
- **Automatic `AfipToken` cleanup.** The TA is cached in `afip_token` for
  the 12 h AFIP TTL. After expiration the row is dead weight. A follow-up
  adds a Celery beat task (daily) that deletes rows where
  `expiration_time < now() - retention_days`, where `retention_days` is a
  small audit window (default 7) so expired tokens stay queryable briefly
  for incident debugging. Keep history is **not** the goal — these rows
  carry no business value.

Tracked in `docs/references/afip/legacy_pending_issues.md` for the agency's
own backlog reference.

---

## Migration plan from legacy Django module

The Django code in `afip/` (gitignored, kept locally as reference) is read-only
during the port. Each commit on the feature branch maps to one of the steps
listed in the PR description. The branch ships when:

1. `make test` is green with coverage ≥80% globally and ≥85% on `shared/afip/`.
2. `make lint` is clean.
3. `pre-commit run --all-files` is clean.
4. The Alembic migration round-trips on a fresh database.
5. A smoke test against AFIP **homologación** (`AFIP_ENVIRONMENT=homo`) issues
   one Factura B successfully and one Factura A is correctly rejected with
   error 10243 against a CF receiver.

The smoke test is documented but run manually by the operator with real
homologación credentials — it cannot live in CI because AFIP homologación
requires a registered cert.
