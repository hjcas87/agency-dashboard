"""
Schemas para el feature de Auth.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema para login."""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, max_length=72, description="Contraseña")


class LoginResponse(BaseModel):
    """Schema para respuesta de login."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: dict = Field(..., description="Información del usuario")


class PasswordResetRequest(BaseModel):
    """Schema para solicitar reseteo de contraseña."""
    email: EmailStr = Field(..., description="Email del usuario")


class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reseteo de contraseña."""
    token: str = Field(..., description="Token de reseteo")
    new_password: str = Field(..., min_length=8, max_length=72, description="Nueva contraseña")


class PasswordChangeRequest(BaseModel):
    """Schema para cambiar contraseña (usuario autenticado)."""
    current_password: str = Field(..., min_length=1, max_length=72, description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=72, description="Nueva contraseña")


class UserCreateWithPassword(BaseModel):
    """Schema para crear usuario con contraseña (solo admin)."""
    email: EmailStr = Field(..., description="Email del usuario")
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del usuario")
    password: str = Field(..., min_length=8, max_length=72, description="Contraseña inicial")
    is_active: bool = Field(default=True, description="Si el usuario está activo")
    is_admin: bool = Field(default=False, description="Si el usuario es administrador")

