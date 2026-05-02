"""
Dependencies para autenticación.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.core.features.users.models import User
from app.core.features.users.repository import UserRepository
from app.database import get_db
from app.shared.constants import AUTH_ERRORS, AUTH_SCHEME, AUTHENTICATE_HEADER, JWT_CLAIM_SUB

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency para obtener el usuario actual autenticado.

    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get(JWT_CLAIM_SUB)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERRORS["invalid_credentials"],
                headers={AUTHENTICATE_HEADER: AUTH_SCHEME},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_ERRORS["invalid_credentials"],
            headers={AUTHENTICATE_HEADER: AUTH_SCHEME},
        )

    user_repo = UserRepository(db)
    user = user_repo.get(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_ERRORS["user_not_found"],
            headers={AUTHENTICATE_HEADER: AUTH_SCHEME},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AUTH_ERRORS["inactive_user"],
        )

    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Dependency para obtener usuario activo.

    Args:
        current_user: Usuario actual

    Returns:
        Usuario activo
    """
    return current_user


# Optional dependency para rutas que pueden ser públicas o privadas
def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: Session = Depends(get_db),
) -> User | None:
    """
    Dependency opcional para obtener usuario si está autenticado.

    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        db: Sesión de base de datos

    Returns:
        Usuario si está autenticado, None si no
    """
    if credentials is None:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
