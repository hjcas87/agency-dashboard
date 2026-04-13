"""
Routes para el feature de Auth.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.features.auth.service import AuthService
from app.core.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    UserCreateWithPassword,
    UserRegister,
)
from app.core.features.auth.dependencies import get_current_active_user
from app.core.features.users.models import User
from app.shared.constants import AUTH_SUCCESS

router = APIRouter(prefix="/auth", tags=["Core: Auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para obtener el service de autenticación."""
    return AuthService(db)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service),
):
    """Register a new user account (public endpoint, no auth required)."""
    user = service.register(user_data)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
    }


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Authenticate a user and return a JWT token."""
    return service.login(login_data)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtiene la información del usuario autenticado.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """
    Cierra sesión del usuario actual.
    Nota: En JWT, el logout se maneja en el cliente eliminando el token.
    Este endpoint puede usarse para logging o invalidación de tokens en el futuro.
    """
    return {"message": AUTH_SUCCESS["logged_out"]}


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
):
    """
    Solicita un reseteo de contraseña.
    Envía un email con un token de reseteo.
    """
    return service.request_password_reset(reset_data)


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    service: AuthService = Depends(get_auth_service),
):
    """
    Confirma el reseteo de contraseña con un token.
    """
    return service.confirm_password_reset(reset_data)


@router.post("/password/change", status_code=status.HTTP_200_OK)
async def change_password(
    change_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Cambia la contraseña del usuario autenticado.
    """
    return service.change_password(current_user.id, change_data)


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user_with_password(
    user_data: UserCreateWithPassword,
    current_user: User = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Crea un nuevo usuario con contraseña (solo para administradores).
    TODO: Agregar verificación de rol de administrador.
    """
    user = service.create_user_with_password(user_data)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }

