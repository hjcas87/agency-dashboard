"""Reusable AFIP/ARCA electronic invoicing integration.

Public API exported here. Implementation details live in submodules
(`auth/`, `transport/`, `billing/`, `taxpayer/`). Consumers must depend
only on this package's exports — direct imports from submodules are an
abstraction leak.

See `README.md` in this directory for the design rationale and
`docs/references/afip/manual_dev.md` for the normative ARCA reference.
"""
