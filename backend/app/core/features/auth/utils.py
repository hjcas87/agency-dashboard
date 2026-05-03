"""
Utilidades para autenticación.
"""
import secrets
from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.core.features.auth.models import PasswordResetToken, UserPassword


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña

    Returns:
        True si la contraseña es correcta
    """
    try:
        # Usar bcrypt directamente para evitar problemas con passlib
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Verificar contraseña
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña usando bcrypt directamente.

    Args:
        password: Contraseña en texto plano (máximo 72 bytes para bcrypt)

    Returns:
        Hash de la contraseña
    """
    # Bcrypt tiene un límite estricto de 72 bytes
    password_bytes = password.encode("utf-8")

    # Truncar a exactamente 72 bytes si es más largo
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generar salt y hash con bcrypt directamente
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Retornar como string
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración (opcional)

    Returns:
        JWT token codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_user_password(db: Session, user_id: int) -> UserPassword | None:
    """
    Obtiene la información de contraseña de un usuario.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        UserPassword si existe, None si no
    """
    return db.query(UserPassword).filter(UserPassword.user_id == user_id).first()


def set_user_password(db: Session, user_id: int, password: str) -> UserPassword:
    """
    Establece o actualiza la contraseña de un usuario.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        password: Contraseña en texto plano

    Returns:
        UserPassword creado o actualizado
    """
    hashed_password = get_password_hash(password)
    user_password = get_user_password(db, user_id)

    if user_password:
        user_password.hashed_password = hashed_password
        user_password.updated_at = datetime.utcnow()
    else:
        user_password = UserPassword(user_id=user_id, hashed_password=hashed_password)
        db.add(user_password)

    db.commit()
    db.refresh(user_password)
    return user_password


def create_password_reset_token(db: Session, user_id: int) -> str:
    """
    Crea un token de reseteo de contraseña.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Token generado
    """
    # Generar token único
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)  # Token válido por 24 horas

    reset_token = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)

    return token


def get_password_reset_token(db: Session, token: str) -> PasswordResetToken | None:
    """
    Obtiene un token de reseteo de contraseña.

    Args:
        db: Sesión de base de datos
        token: Token a buscar

    Returns:
        PasswordResetToken si existe y es válido, None si no
    """
    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow(),
        )
        .first()
    )

    return reset_token
