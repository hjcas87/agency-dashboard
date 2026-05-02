"""
Base PDF renderer interface.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from app.shared.pdf.template import PdfTemplate


class PdfRenderer(ABC):
    """Interface for document-specific PDF renderers."""

    # Page margins in millimeters: (top, right, bottom, left).
    # Renderers can override to fit their layout — e.g. AFIP receipts
    # extend almost edge-to-edge, while proposals keep generous margins.
    page_margins_mm: tuple[float, float, float, float] = (25, 20, 25, 20)

    @abstractmethod
    def render(self, data: dict, template: PdfTemplate) -> list[Any]:
        """
        Render the document into a list of reportlab flowables (the
        "story" passed to `SimpleDocTemplate.build`).

        Args:
            data: Document-specific data (varies by renderer).
            template: PDF template with styling configuration.

        Returns:
            List of reportlab flowables (Paragraph, Table, Spacer, …).
        """

    def make_page_callback(
        self, data: dict, template: PdfTemplate
    ) -> Callable[[Any, Any], None] | None:
        """
        Build an optional `(canvas, doc) -> None` callback that draws
        fixed-position elements (e.g. a footer pinned to the bottom of
        the page) every time a new page is started.

        Renderers that don't need fixed-position drawing return None.
        """
        return None
