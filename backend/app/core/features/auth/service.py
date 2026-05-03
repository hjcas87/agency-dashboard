"""
Service layer para el feature de Auth.
"""
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.features.auth.schemas import (
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    UserCreateWithPassword,
    UserRegister,
)
from app.core.features.auth.tasks import send_email_task
from app.core.features.auth.utils import (
    create_access_token,
    create_password_reset_token,
    get_password_reset_token,
    get_user_password,
    set_user_password,
    verify_password,
)
from app.core.features.users.models import User
from app.core.features.users.repository import UserRepository
from app.shared.constants import (
    AUTH_ERRORS,
    AUTH_SUCCESS,
    JWT_CLAIM_SUB,
    TOKEN_TYPE,
)


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
                detail=AUTH_ERRORS["invalid_credentials"],
            )

        # Verificar contraseña
        user_password = get_user_password(self.db, user.id)
        if not user_password or not verify_password(
            login_data.password, user_password.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["invalid_credentials"],
            )

        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AUTH_ERRORS["inactive_user"],
            )

        # Crear token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={JWT_CLAIM_SUB: str(user.id)}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": TOKEN_TYPE,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
            },
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
            return {"message": AUTH_SUCCESS["password_reset_sent"]}

        # Crear token de reseteo
        token = create_password_reset_token(self.db, user.id)

        # Preparar contenido del email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        subject = "Password Reset"
        body = f"""
Hola {user.name},

Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:

{reset_url}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, puedes ignorar este email.

Saludos,
{settings.EMAIL_FROM_NAME}
"""
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .button:hover {{ background-color: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Restablecer Contraseña</h2>
        <p>Hola {user.name},</p>
        <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente botón para crear una nueva contraseña:</p>
        <a href="{reset_url}" class="button">Restablecer Contraseña</a>
        <p>O copia y pega este enlace en tu navegador:</p>
        <p style="word-break: break-all; color: #666;">{reset_url}</p>
        <p>Este enlace expirará en 1 hora.</p>
        <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
        <p>Saludos,<br>{settings.EMAIL_FROM_NAME}</p>
    </div>
</body>
</html>
"""

        # Encolar email en background usando Celery
        # Esto no bloquea la respuesta de la API
        try:
            send_email_task.delay(
                to=user.email,
                subject=subject,
                body=body,
                html_body=html_body,
            )
        except Exception as e:
            # Log del error pero no fallar la respuesta
            # El email se reintentará automáticamente por Celery
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error al encolar email de password reset: {str(e)}")

        return {"message": AUTH_SUCCESS["password_reset_sent"]}

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
                detail=AUTH_ERRORS["invalid_token"],
            )

        # Actualizar contraseña
        set_user_password(self.db, int(reset_token.user_id), reset_data.new_password)

        # Marcar token como usado
        reset_token.used = True
        self.db.commit()

        return {"message": AUTH_SUCCESS["password_reset_done"]}

    def change_password(self, user_id: int, change_data: PasswordChangeRequest) -> dict:
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
            change_data.current_password, user_password.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AUTH_ERRORS["incorrect_password"],
            )

        # Actualizar contraseña
        set_user_password(self.db, user_id, change_data.new_password)

        return {"message": AUTH_SUCCESS["password_changed"]}

    def register(self, user_data: UserRegister) -> User:
        """
        Public user registration (self-signup).

        Args:
            user_data: Registration data (email, name, password).

        Returns:
            Created user.

        Raises:
            HTTPException: If email already exists.
        """
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AUTH_ERRORS["email_already_exists"],
            )

        from app.core.features.users.schemas import UserCreate

        user_create = UserCreate(
            email=user_data.email,
            name=user_data.name,
            is_active=True,
        )
        user = self.user_repository.create(user_create.model_dump())
        set_user_password(self.db, user.id, user_data.password)
        return user

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
                detail=AUTH_ERRORS["user_exists_detail"].format(email=user_data.email),
            )

        # Crear usuario
        from app.core.features.users.schemas import UserCreate

        user_create = UserCreate(
            email=user_data.email, name=user_data.name, is_active=user_data.is_active
        )
        user = self.user_repository.create(user_create.model_dump())

        # Establecer contraseña
        set_user_password(self.db, user.id, user_data.password)

        return user
