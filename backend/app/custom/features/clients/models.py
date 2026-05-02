"""
SQLAlchemy models for the Client feature.

Uses SQLAlchemy 2.x `Mapped[...]` / `mapped_column(...)` declarations
so attribute access yields plain types instead of `Column[T]`.
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base
from app.shared.afip.enums import IvaCondition


class Client(Base):
    """Client model representing a business contact.

    AFIP-related fields (`cuit`, `iva_condition`) are optional. Forks
    that do not invoice with ARCA can leave them NULL forever; the rest
    of the app does not depend on them. The IvaCondition enum reused
    here comes from `shared/afip/enums` — single source of truth across
    invoicing and client data.
    """

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Free-form fiscal address — printed verbatim on the invoice PDF
    # under "Domicilio". Auto-populated from the AFIP padrón lookup
    # (concatenated address + locality + province) but the operator can
    # override it manually before saving.
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # AFIP — both optional. CUIT is 11 digits without separators; the
    # schema/service layer normalizes user input before persisting here.
    cuit: Mapped[str | None] = mapped_column(String(11), nullable=True, index=True)
    iva_condition: Mapped[IvaCondition | None] = mapped_column(String(2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', email='{self.email}')>"
