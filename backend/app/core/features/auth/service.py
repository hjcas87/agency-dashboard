"""
Service layer para el feature de Auth.
"""
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.features.users.models import User
from app.core.features.users.repository import UserRepository
from app.core.features.auth.schemas import (
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    UserCreateWithPassword,
)
from app.core.features.auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_user_password,
    set_user_password,
    create_password_reset_token,
    get_password_reset_token,
)
from app.core.features.auth.models import PasswordResetToken


class AuthService:
    """Service para manejar lógica de negocio de autenticación."""

    def __init__(self, db: Session):
        """
        Inicializa el service.
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.user_repository = UserRepository(db)

    def login(self, login_data: LoginRequest) -> dict:
        """
        Autentica un usuario y genera un token JWT.
        
        Args:
            login_data: Datos de login
            
        Returns:
            Dict con access_token, token_type y user
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        # Buscar usuario por email
        user = self.user_repository.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        # Verificar contraseña
        user_password = get_user_password(self.db, user.id)
        if not user_password or not verify_password(login_data.password, user_password.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        
        # Crear token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
            }
        }

    def request_password_reset(self, reset_data: PasswordResetRequest) -> dict:
        """
        Solicita un reseteo de contraseña.
        
        Args:
            reset_data: Datos de solicitud de reseteo
            
        Returns:
            Dict con mensaje de confirmación
        """
        user = self.user_repository.get_by_email(reset_data.email)
        if not user:
            # Por seguridad, no revelamos si el email existe o no
            return {"message": "If the email exists, a password reset link has been sent"}
        
        # Crear token de reseteo
        token = create_password_reset_token(self.db, user.id)
        
        # TODO: Enviar email con el token
        # Por ahora, retornamos el token en la respuesta (solo para desarrollo)
        # En producción, esto debe enviarse por email
        
        return {
            "message": "If the email exists, a password reset link has been sent",
            "token": token  # Solo para desarrollo, remover en producción
        }

    def confirm_password_reset(self, reset_data: PasswordResetConfirm) -> dict:
        """
        Confirma el reseteo de contraseña con un token.
        
        Args:
            reset_data: Datos de confirmación de reseteo
            
        Returns:
            Dict con mensaje de confirmación
            
        Raises:
            HTTPException: Si el token es inválido o expiró
        """
        # Buscar token
        reset_token = get_password_reset_token(self.db, reset_data.token)
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )
        
        # Actualizar contraseña
        set_user_password(self.db, int(reset_token.user_id), reset_data.new_password)
        
        # Marcar token como usado
        reset_token.used = True
        self.db.commit()
        
        return {"message": "Password has been reset successfully"}

    def change_password(
        self,
        user_id: int,
        change_data: PasswordChangeRequest
    ) -> dict:
        """
        Cambia la contraseña de un usuario autenticado.
        
        Args:
            user_id: ID del usuario
            change_data: Datos de cambio de contraseña
            
        Returns:
            Dict con mensaje de confirmación
            
        Raises:
            HTTPException: Si la contraseña actual es incorrecta
        """
        # Verificar contraseña actual
        user_password = get_user_password(self.db, user_id)
        if not user_password or not verify_password(
            change_data.current_password,
            user_password.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        
        # Actualizar contraseña
        set_user_password(self.db, user_id, change_data.new_password)
        
        return {"message": "Password has been changed successfully"}

    def create_user_with_password(self, user_data: UserCreateWithPassword) -> User:
        """
        Crea un usuario con contraseña (solo para administradores).
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            Usuario creado
            
        Raises:
            HTTPException: Si el email ya existe
        """
        # Verificar si el email ya existe
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user_data.email} already exists",
            )
        
        # Crear usuario
        from app.core.features.users.schemas import UserCreate
        user_create = UserCreate(
            email=user_data.email,
            name=user_data.name,
            is_active=user_data.is_active
        )
        user = self.user_repository.create(user_create.model_dump())
        
        # Establecer contraseña
        set_user_password(self.db, user.id, user_data.password)
        
        return user

