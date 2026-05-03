"""
SQLAlchemy models for the Client feature.

Uses SQLAlchemy 2.x `Mapped[...]` / `mapped_column(...)` declarations
so attribute access yields plain types instead of `Column[T]`.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
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

    `email` is the **primary** contact email (used as `to:` when sending
    proposals/invoices). Additional addressees — accountancy, finance,
    secretaries who must always be CC'd — live in `additional_emails`
    and are appended to `cc:` automatically by the email send route.
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

    additional_emails: Mapped[list["ClientEmail"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
        order_by="ClientEmail.id",
    )

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


class ClientEmail(Base):
    """Secondary email address for a client.

    The client's `email` column stays as the primary contact (`to:` in
    sends). This table holds *additional* recipients that must always
    be CC'd when reaching out — typically accountancy / treasury /
    secretaries. The `label` is a free-form note ("Tesorería",
    "Administración") so the operator can recognise each row in the
    edit form, but it doesn't affect routing.
    """

    __tablename__ = "client_emails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    client: Mapped["Client"] = relationship(back_populates="additional_emails")

    def __repr__(self) -> str:
        return (
            f"<ClientEmail(id={self.id}, client_id={self.client_id}, "
            f"email='{self.email}', label='{self.label}')>"
        )
