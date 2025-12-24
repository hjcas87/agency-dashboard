"""
Modelos para el feature de Auth.
Extiende el modelo User de core con campos de autenticación.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base
from app.core.features.users.models import User


class UserPassword(Base):
    """Modelo para almacenar contraseñas de usuarios."""
    __tablename__ = "user_passwords"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="password_info")

    def __repr__(self):
        return f"<UserPassword(user_id={self.user_id})>"


class PasswordResetToken(Base):
    """Modelo para tokens de reseteo de contraseña."""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, expires_at={self.expires_at})>"

