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
