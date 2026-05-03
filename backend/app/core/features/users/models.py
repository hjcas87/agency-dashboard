"""
Modelos para el feature de Users.
"""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """Roles de usuario."""

    ADMIN = "ADMIN"
    VENDEDOR = "VENDEDOR"


class User(Base):
    """Modelo de Usuario."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole, name="userrole"), nullable=False, server_default="VENDEDOR")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
