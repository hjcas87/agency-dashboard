"""
Shared PDF generation module.

Provides a reusable PDF generator that can be consumed by any feature
(proposals, invoices, reports, etc.) without depending on specific features.

Structure:
    models.py       - SQLAlchemy model (no external deps)
    schemas.py      - Pydantic schemas
    template.py     - Repository + CRUD
    generator.py    - PdfGenerator (depends on weasyprint)
    renderers/      - Document-specific renderers
"""
