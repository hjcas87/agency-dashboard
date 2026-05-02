# Architecture Decisions

> This document needs to be completed.

## Record of Architectural Decisions

### ADR-0001: Feature-Based Architecture
**Status**: Accepted
**Date**: 2025-04-11

**Decision**: Use feature-based organization instead of layer-based.
**Context**: Need clear separation between core (reusable) and custom (client-specific) code.
**Consequences**: Each feature is self-contained but requires more initial setup.

### ADR-0002: Core/Custom Separation
**Status**: Accepted
**Date**: 2025-04-11

**Decision**: Split code into `core/` (stable, generic) and `custom/` (client-specific).
**Context**: Enable fork-friendly development where core can be updated without breaking customizations.
**Consequences**: Requires discipline to not mix concerns.

### ADR-0003: Message Broker — RabbitMQ
**Status**: Accepted
**Date**: 2025-04-11

**Decision**: Use RabbitMQ instead of Kafka for Celery message broker.
**Context**: Simpler setup, lighter resource usage, better fit for Celery.
**Consequences**: No Kafka dependency; RabbitMQ management UI available.

### ADR-0004: Python 3.12 Minimum
**Status**: Accepted
**Date**: 2025-04-11

**Decision**: Require Python 3.12 as minimum version.
**Context**: Python 3.14 lacks no wheels for key packages (pydantic, etc). Python 3.12 is stable and production-ready.
**Consequences**: Better package compatibility, no compilation issues.

### ADR-0005: psycopg v3 over psycopg2
**Status**: Accepted
**Date**: 2025-04-11

**Decision**: Use `psycopg[binary]` (v3) instead of `psycopg2-binary`.
**Context**: psycopg2 requires `pg_config` to compile on some systems. psycopg v3 has pre-built wheels.
**Consequences**: No system dependencies needed for PostgreSQL driver.

### ADR-0006: AFIP/ARCA integration as a shared service
**Status**: Accepted
**Date**: 2026-05-01

**Decision**: Implement the AFIP/ARCA electronic invoicing integration (WSAA + WSFEv1 + Padrón A5 + FCE MiPyMEs) as a reusable shared service at `backend/app/shared/afip/`, mirroring the shape of `shared/email/` and `shared/pdf/`. The service exposes no HTTP routes — only a typed Python API consumed by custom feature services (e.g. `custom/features/invoices/`).

**Context**: A working Django implementation exists in production (3.5k LOC). It is read-only reference now (path `afip/` is `.gitignore`d). The integration must be reusable across Argentine clients of the agency (multiple forks consume it), so it cannot live in `core/features/` (which would force every fork to ship it whether they need it or not) and cannot live in `custom/features/` (which would lock it to one client). It also cannot define HTTP routes, because the consumer of the service decides when and how to invoice — `shared/afip/` is a library, not a feature.

**Consequences**:
- Every Argentine client fork can call into `app.shared.afip.service` without changes to core; non-Argentine forks ignore it.
- The persistent `Invoice` business entity stays out of `shared/afip/`. `shared/afip/models.py` only persists what AFIP itself returns — `AfipToken` (WSAA TA cache) and `AfipInvoiceLog` (audit trail of what was sent and received). The client's `Invoice` model lives in `custom/features/invoices/` and references `AfipInvoiceLog` by FK. This is the deviation from the legacy Django module, which had `Invoice` directly tied to `Quote`.
- Configuration is driven by env vars (`AFIP_CUIT`, `AFIP_POINT_OF_SALE`, `AFIP_CERT_PATH`, `AFIP_KEY_PATH`, `AFIP_ENVIRONMENT`, `AFIP_CURRENCY_ID`); cert and key files live outside the repo (path is configurable, gitignored when local).
- CMS signing migrates from `openssl smime -sign` (subprocess on system binary) to `cryptography.hazmat.primitives.cms` (already a backend dependency). HTTP client migrates from `requests` to `httpx` with a custom `ssl.SSLContext` configured to `SECLEVEL=1` (required because AFIP servers still negotiate legacy DH keys). XML construction stops using f-strings; `lxml` is used to guarantee escape and well-formedness.
- Detailed design lives at `backend/app/shared/afip/README.md`. Normative reference (ARCA manual RG 4291 v4.0) lives at `docs/references/afip/`.
