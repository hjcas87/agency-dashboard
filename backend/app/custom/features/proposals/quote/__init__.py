"""
Quote PDF generation — overlays dynamic data on top of 5 base PDF assets.

The base PDFs (cover, quote, deliverables, terms, final) are designed
in a separate tool and shipped under `assets/`. This module only
adds the dynamic content layer (text fields, paginated lists) and
merges everything into the final client-facing booklet.
"""
