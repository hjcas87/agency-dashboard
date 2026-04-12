"""
SQLAlchemy models for Tiendanube connection feature.

Models:
- Store: Represents a connected Tiendanube store
- TiendanubeToken: Encrypted token storage for security
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class StoreStatus(str, enum.Enum):
    """Status of a connected Tiendanube store."""

    ACTIVE = "active"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class Store(Base):
    """Represents a Tiendanube store connected to Mendri Loyalty."""

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tiendanube_store_id = Column(String(50), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=True)
    currency = Column(String(10), nullable=True, default="ARS")
    status = Column(
        Enum(StoreStatus, name="storestatus"),
        nullable=False,
        server_default="active",
    )
    # OAuth credentials (encrypted, stored in TiendanubeToken, not here)
    is_active = Column(Boolean, nullable=False, server_default="true")
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("tiendanube_store_id", name="uq_store_tiendanube_id"),
    )

    def __repr__(self):
        return f"<Store(id={self.id}, name='{self.name}', status={self.status.value})>"


class TiendanubeToken(Base):
    """Stores encrypted Tiendanube OAuth tokens per store."""

    __tablename__ = "tiendanube_tokens"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(
        Integer, nullable=False, index=True, unique=True
    )
    encrypted_access_token = Column(Text, nullable=False)
    token_type = Column(String(50), nullable=False, default="bearer")
    scope = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<TiendanubeToken(store_id={self.store_id})>"
